import tempfile
import os
import pytest
from src.db.sqlite import init_db

@pytest.fixture(autouse=True)
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        os.environ["DB_PATH"] = tmp.name
        init_db()
        yield
        os.environ.pop("DB_PATH")
