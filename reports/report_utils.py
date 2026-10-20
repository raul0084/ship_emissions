"""Helpers for the ship-emissions report (``reports/emissions_report.qmd``).

Everything that is not narrative lives here, so the report stays readable and
the logic can be tested on its own. Functions take DataFrames and return
DataFrames or figures; none of them read global state.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
INK = "#0f2a43"       # deep navy: text, primary bars
TEAL = "#1b7f8c"      # secondary series
AMBER = "#c9792b"     # warnings, thresholds
SAND = "#d9c49a"      # tertiary series
MUTED = "#8a96a3"     # axes, de-emphasised marks
GRID = "#e3e8ee"

TOTAL_SUFFIX = " total (t)"
DISPLAY_NAMES = {"SFOC": "Fuel consumption", "CO2": "CO₂"}
MODES = {"nav": "Navigation", "mani": "Manoeuvring", "hot": "Hotelling"}
FALLBACK_LABELS = {"default", "unmatched", "unknown", "nan", "none", "<na>"}

_MODE_COL = re.compile(
    r"^E_(?P<mode>nav|mani|hot)[a-z]*_(?P<pollutant>.+?)"
    r"(?:_(?P<unit>g|t)|\s*\((?P<unit2>g|t)\))?$",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------
# Project plumbing
# --------------------------------------------------------------------------
def find_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` until a directory containing ``core/`` is found."""
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "core").is_dir():
            return candidate
    raise FileNotFoundError(
        f"Could not find a 'core/' package above {start}. "
        "Render the report from inside the repository."
    )


def add_to_path(root: Path) -> None:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def require_columns(df: pd.DataFrame, columns: list[str], where: str) -> None:
    """Fail early, with a readable message, if expected columns are missing."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(
            f"{where}: missing columns {missing}. "
            f"Available columns: {sorted(map(str, df.columns))}"
        )


def load_inputs(calls_path: Path, vessels_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read both CSVs, keeping identifiers as strings (IMO/MMSI must not become floats)."""
    dtypes = {"imo": "string", "mmsi": "string"}
    return (
        pd.read_csv(calls_path, dtype=dtypes),
        pd.read_csv(vessels_path, dtype=dtypes),
    )


# --------------------------------------------------------------------------
# Port-stay durations
# --------------------------------------------------------------------------
def add_stay_hours(
    df: pd.DataFrame, arrival: str = "etautc", departure: str = "etdutc"
) -> pd.DataFrame:
    """Parse timestamps and add ``port_stay_hours`` (NaN where unparseable)."""
    out = df.copy()
    out[arrival] = pd.to_datetime(out[arrival], errors="coerce")
    out[departure] = pd.to_datetime(out[departure], errors="coerce")
    out["port_stay_hours"] = (out[departure] - out[arrival]).dt.total_seconds() / 3600
    return out


def classify_durations(hours: pd.Series, max_stay: float) -> pd.Series:
    """Label each call: valid / missing / departure before arrival / zero / long."""
    status = pd.Series("valid", index=hours.index, dtype="object")
    status[hours == 0] = "zero duration"
    status[hours > max_stay] = "long stay"
    status[hours < 0] = "departure before arrival"
    status[hours.isna()] = "missing timestamp"
    return status


def duration_quantiles(hours: pd.Series) -> pd.DataFrame:
    h = hours[hours.notna() & (hours >= 0)]
    return pd.DataFrame(
        {
            "Statistic": ["Median", "90th percentile", "95th percentile", "Maximum"],
            "Hours": [h.median(), h.quantile(0.90), h.quantile(0.95), h.max()],
        }
    )


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------
def label(name: str) -> str:
    return DISPLAY_NAMES.get(name, name)


def total_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if str(c).endswith(TOTAL_SUFFIX)]


def pollutant_name(col: str) -> str:
    return col[: -len(TOTAL_SUFFIX)]


def coverage_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calls per match source, as reported by the pipeline itself."""
    source = df["match_source"].astype("string").str.lower().fillna("unknown")
    out = source.value_counts().rename_axis("Match source").reset_index(name="Calls")
    out["Share (%)"] = 100 * out["Calls"] / out["Calls"].sum()
    return out


def fallback_share(df: pd.DataFrame) -> float:
    """Fraction of calls that used fallback vessel data."""
    source = df["match_source"].astype("string").str.lower().fillna("unknown")
    return float(source.isin(FALLBACK_LABELS).mean())


def pollutant_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total and propagated uncertainty per pollutant.

    Per-call sigmas are combined in quadrature, i.e. errors are treated as
    independent between calls. See the limitations section of the report.
    """
    rows = []
    for col in total_columns(df):
        name = pollutant_name(col)
        sigma_col = f"σ {name} (t)"
        total = pd.to_numeric(df[col], errors="coerce").sum(min_count=1)
        if sigma_col in df.columns:
            sigma = float(np.sqrt((pd.to_numeric(df[sigma_col], errors="coerce") ** 2).sum()))
        else:
            sigma = np.nan
        rows.append(
            {
                "key": name,
                "Pollutant": label(name),
                "Total (t)": total,
                "σ (t)": sigma,
                "σ (%)": 100 * sigma / total if total else np.nan,
            }
        )
    return pd.DataFrame(rows)


def threshold_sensitivity(
    df: pd.DataFrame,
    thresholds: list[float],
    baseline: float,
    hours_col: str = "port_stay_hours",
) -> pd.DataFrame:
    """Totals per pollutant for each maximum-stay cut-off, plus change vs baseline."""
    cols = total_columns(df)
    n_all = len(df)
    rows = []
    for t in sorted(set([*thresholds, baseline])):
        kept = df[df[hours_col].between(0, t)]
        row = {
            "Max stay (h)": t,
            "Included calls": len(kept),
            "Excluded (%)": 100 * (1 - len(kept) / n_all) if n_all else np.nan,
        }
        for c in cols:
            row[pollutant_name(c)] = pd.to_numeric(kept[c], errors="coerce").sum(min_count=1)
        rows.append(row)
    return pd.DataFrame(rows)


def relative_to_baseline(sens: pd.DataFrame, baseline: float) -> pd.DataFrame:
    """Percentage change of each pollutant total relative to the baseline cut-off."""
    pollutants = [c for c in sens.columns if c not in ("Max stay (h)", "Included calls", "Excluded (%)")]
    base = sens.loc[sens["Max stay (h)"] == baseline, pollutants].iloc[0]
    out = sens[["Max stay (h)"]].copy()
    for p in pollutants:
        out[p] = 100 * (sens[p] / base[p] - 1)
    return out




def mode_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate fuel consumption and emissions by operating mode.

    Expects labelled columns such as 'CO nav (t)',
    'NOx mani (t)', and 'SFOC hotelling (t)'.
    CO2 is derived from mode-specific SFOC and the fuel carbon factor.
    """
    modes = {
        "Navigation": "nav",
        "Manoeuvring": "mani",
        "Hotelling": "hotelling",
    }

    metrics = ["CO", "NOx", "NMVOC", "TSP/PM", "BC", "SFOC"]
    rows = {}

    for metric in metrics:
        mode_totals = {}

        for mode, suffix in modes.items():
            col = f"{metric} {suffix} (t)"

            if col in df.columns:
                mode_totals[mode] = pd.to_numeric(
                    df[col], errors="coerce"
                ).sum()
            else:
                mode_totals[mode] = 0.0

        # Include only metrics present in the pipeline output.
        if any(f"{metric} {suffix} (t)" in df.columns
               for suffix in modes.values()):
            rows[metric] = mode_totals

    result = pd.DataFrame.from_dict(rows, orient="index")
    result = result.reindex(columns=list(modes.keys()), fill_value=0.0)

    # Derive CO2 by mode from fuel consumption, using the same
    # carbon factors as calculate_uncertainty().
    if "fuel" in df.columns and "SFOC" in result.index:
        fuel = df["fuel"].astype("string").str.lower()
        cf = pd.Series(
            np.where(fuel.eq("lng"), 2.750, 3.206),
            index=df.index,
        )

        co2_totals = {}
        for mode, suffix in modes.items():
            col = f"SFOC {suffix} (t)"

            if col in df.columns:
                fuel_by_call = pd.to_numeric(
                    df[col], errors="coerce"
                )
                co2_totals[mode] = (fuel_by_call * cf).sum()
            else:
                co2_totals[mode] = 0.0

        rows["CO2"] = co2_totals
        result = pd.DataFrame.from_dict(rows, orient="index")
        result = result.reindex(columns=list(modes.keys()), fill_value=0.0)

    return result




def mode_shares(breakdown: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage shares by pollutant and operating mode."""
    if breakdown.empty:
        return pd.DataFrame()

    mode_columns = [
        mode for mode in ("Navigation", "Manoeuvring", "Hotelling")
        if mode in breakdown.columns
    ]

    if not mode_columns:
        return pd.DataFrame()

    shares = breakdown[mode_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    totals = shares.sum(axis=1).replace(0, np.nan)

    return shares.div(totals, axis=0) * 100



def vessel_label(df: pd.DataFrame) -> pd.Series:
    """'Name (IMO)' where an IMO exists, otherwise just the name."""
    name = df["Vessel name"].astype("string").str.strip()
    imo = df["IMO"].astype("string").str.strip().replace("", pd.NA)
    return name.where(imo.isna(), name + " (" + imo + ")")


def rank_groups(df: pd.DataFrame, group_col: str, value_col: str, top_n: int = 12) -> pd.DataFrame:
    """Top groups by total emissions, with calls, mean per call and share of total."""
    data = df.dropna(subset=[group_col])
    grouped = data.groupby(group_col, observed=True)[value_col]
    out = pd.DataFrame({"Port calls": grouped.size(), "Total (t)": grouped.sum(min_count=1)})
    out["Mean per call (t)"] = out["Total (t)"] / out["Port calls"]
    out["Share of total (%)"] = 100 * out["Total (t)"] / df[value_col].sum()
    return out.sort_values("Total (t)", ascending=False).head(top_n)


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------
def apply_style() -> None:
    mpl.rcParams.update(
        {
            "figure.figsize": (9, 4.6),
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.titlelocation": "left",
            "axes.titleweight": "bold",
            "axes.titlesize": 12,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "legend.frameon": False,
            "axes.prop_cycle": mpl.cycler(color=[INK, TEAL, AMBER, SAND, MUTED]),
        }
    )


def plot_ranking(ranking: pd.DataFrame, ylabel: str, xlabel: str):
    """Horizontal bar chart of a ``rank_groups`` result, largest at the top."""
    data = ranking["Total (t)"].iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, max(3, 0.36 * len(data) + 1)))
    ax.barh(data.index.astype(str), data.values, color=INK)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", visible=False)
    return fig


def show_table(df: pd.DataFrame, formats: dict | None = None, index: bool = False):
    """Styled DataFrame for HTML output."""
    styler = df.style.format(formats or {}, na_rep="–")
    if not index:
        styler = styler.hide(axis="index")
    return styler



