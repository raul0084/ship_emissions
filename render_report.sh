
#!/usr/bin/env bash
set -euo pipefail

# Resolve project root from this script's location
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults (overridable via command-line arguments)
OUTPUT="${1:-ship_emissions_report_test.html}"
VESSELS="${2:-data/tests/vessels_2012.csv}"
PORT_CALLS="${3:-data/tests/port_calls_2012.csv}"
AUTHOR="Raúl Ávila"

# Ensure the output directory exists
mkdir -p "$PROJECT_ROOT/reports/archive"

docker run --rm \
  -v "$PROJECT_ROOT:/app" \
  -w /app/reports \
  emissiones-report \
  render emissions_report.qmd \
  --output-dir archive \
  -o "$OUTPUT" \
  -M "author=${AUTHOR}" \
  -P "vessels:${VESSELS}" \
  -P "port_calls:${PORT_CALLS}"
