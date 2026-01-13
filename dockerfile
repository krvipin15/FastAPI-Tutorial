# ============================
# Builder stage
# This stage installs all dependencies and tools needed to *build* the app.
# Nothing from here is shipped except what is strictly required at runtime.
# ============================
FROM python:3.12-slim AS builder

# Avoid writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# All build work happens here
WORKDIR /build

# Install only what we need to fetch and build dependencies
# --no-install-recommends keeps the layer small
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv


# Copy dependency manifests first so Docker can cache this layer
COPY pyproject.toml uv.lock ./

# Resolve and install dependencies into uv's managed environment
# Cache is mounted so repeated builds are fast
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras


# ============================
# Runtime stage
# This is the image that actually runs in production.
# It contains only Python, uv, resolved deps, and your app.
# ============================
FROM python:3.12-slim

# Same runtime-safe Python settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Where your app lives in the container
WORKDIR /usr/src/app

# Copy only the uv environment and binaries from the builder
# This avoids shipping build tools like curl/git/apt
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /root/.local /root/.local

# Copy your application source code (excluding files matched by .dockerignore)
COPY . .

# Ensure uv is available
ENV PATH="/root/.local/bin:$PATH"

# Start FastAPI in production mode
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
