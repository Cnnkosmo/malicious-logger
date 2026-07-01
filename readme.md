# my lil logger

## setup

```bash
install all dependencies (runtime + dev)
uv sync --all-groups
```


```bash
# ingest all sources
uv run python -m malicious_logger 

# ingest a specific source
uv run python -m malicious_logger ingest --source <ursource>

```

## testing

```bash
# unit tests only (no Docker needed)
uv run pytest tests/unit

# all tests including integration (requires Docker running to spin up local postrgress)
uv run pytest

```

## ocal database

```bash
docker compose up -d

uv run alembic upgrade head
```

