# Stage 1: .NET 8 SDK for DllReflector build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet-build
WORKDIR /build
COPY tools/DllReflector/ ./DllReflector/
RUN dotnet publish DllReflector/DllReflector.csproj -c Release -o /app/DllReflector --nologo

# Stage 2: Python runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install .NET 8 runtime for DllReflector execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    libicu-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install .NET 8 runtime — pinned version, downloaded then executed (not piped).
# Using official Microsoft installer script. The channel is pinned to 8.0 so
# only patch-level updates are applied; a major version change requires a
# deliberate Dockerfile update and review.
ENV DOTNET_CHANNEL=8.0
RUN curl -sSL -o /tmp/dotnet-install.sh https://dot.net/v1/dotnet-install.sh \
    && chmod +x /tmp/dotnet-install.sh \
    && /tmp/dotnet-install.sh \
        --channel ${DOTNET_CHANNEL} \
        --runtime dotnet \
        --install-dir /usr/local/dotnet \
    && rm /tmp/dotnet-install.sh
ENV PATH="/usr/local/dotnet:${PATH}"
ENV DOTNET_ROOT="/usr/local/dotnet"

# Copy DllReflector binary
COPY --from=dotnet-build /app/DllReflector ./DllReflector/

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

# Copy application source
COPY src/ ./src/
COPY pipeline/ ./pipeline/

# Environment
ENV PYTHONPATH=/app/src
ENV PLUGIN_EXAMPLES_LOG_FORMAT=json

# Default: run doctor check (safe, non-destructive)
ENTRYPOINT ["python", "-m", "plugin_examples"]
CMD ["doctor"]
