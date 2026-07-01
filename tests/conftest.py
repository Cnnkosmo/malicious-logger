import os

import pytest

# ensure settings can be instantiated in tests without a real .env
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://test:test@localhost:5432/test")
