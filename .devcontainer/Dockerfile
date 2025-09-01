ARG VARIANT="3.11"
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install PostgreSQL client and build deps for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install basic tooling
RUN pip install --upgrade pip

# Create a non-root user (vscode image already includes 'vscode')
USER vscode

WORKDIR /workspace
