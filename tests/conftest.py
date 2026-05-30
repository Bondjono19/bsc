import os
print("loaded test confn")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB", "test")

from unittest.mock import MagicMock
import sqlalchemy.ext.asyncio
sqlalchemy.ext.asyncio.create_async_engine = MagicMock()