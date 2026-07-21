FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md .
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8080
CMD ["uv", "run", "-m", "consumer.main"]
