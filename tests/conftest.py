"""Add import context."""

import pytest

from src.api_v1 import app


@pytest.fixture
def client():
    """Provide the client session used by tests."""
    with app.test_client() as client:
        yield client
