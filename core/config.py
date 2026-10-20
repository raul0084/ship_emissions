from pathlib import Path
import json

BASE_PATH = Path(__file__).resolve().parents[1]

def load_json(name):
    candidates = [
        Path.cwd() / "data" / name,
        Path(__file__).resolve().parents[1] / "data" / name,
        Path("/app/data") / name,
    ]

    for path in candidates:
        if path.is_file():
            with open(path, encoding="utf-8") as f:
                return json.load(f)

    checked_paths = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"Could not find {name}. Checked:\n{checked_paths}"
    )

def default_emission_factors():
    return load_json("emission_factors.json")

def default_uncertainties():
    return load_json("uncertainties.json")

def validate_calls(df):
    required = {"vaixellnom", "etautc", "imo", "mmsi", "etdutc", "terminalnom", "consignatari"}
    missing = required - set(df.columns)
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""

def validate_vaixells(df):
    required = {"vaixellnom", "imo", "mmsi", "fuel", "p_main", "p_aux", "p_gt", "eslora_metres"}
    missing = required - set(df.columns)
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""