FROM python:3.13-slim-bullseye

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies without the project itself (avoids re-running on source changes)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and install the project
COPY README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev --no-editable

EXPOSE 8000

ENTRYPOINT ["/app/.venv/bin/gwas-mcp"]
CMD ["--transport", "http"]
