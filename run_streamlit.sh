
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_NAME="emissiones-streamlit"
DOCKERFILE="Dockerfile.streamlit"

echo "Building Streamlit image..."
docker build \
  -f "$PROJECT_ROOT/$DOCKERFILE" \
  -t "$IMAGE_NAME" \
  "$PROJECT_ROOT"

echo "Starting Streamlit..."
docker run --rm \
  -p 8501:8501 \
  --env-file "$PROJECT_ROOT/.env" \
  -v "$PROJECT_ROOT/data:/app/data" \
  "$IMAGE_NAME"
