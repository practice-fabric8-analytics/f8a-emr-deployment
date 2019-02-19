"""Add import context."""

import sys
import pytest
from pathlib import Path

# src = Path(__file__).resolve().parents[1]
# sys.path.insert(0, str(src))

from src.api_v1 import app

@pytest.fixture
def client():
    """Provide the client session used by tests."""
    with app.test_client() as client:
        yield client