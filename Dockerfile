
FROM python:3.11-slim-bookworm

ARG QUARTO_VERSION=1.10.19

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies and Quarto
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fonts-dejavu-core \
        libfontconfig1 \
        libfreetype6 && \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    curl -fsSL \
      "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${arch}.deb" \
      -o /tmp/quarto.deb; \
    apt-get update; \
    apt-get install -y --no-install-recommends /tmp/quarto.deb; \
    rm -f /tmp/quarto.deb; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the Python project
COPY pyproject.toml .
COPY core/ ./core/
COPY app/ ./app/

RUN pip install --no-cache-dir .

# Allow commands such as:
# docker run ... emissiones-report render ...
ENTRYPOINT ["quarto"]
