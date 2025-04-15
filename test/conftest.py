import sys
import os

import pytest
from starlette.testclient import TestClient

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, src_path)
print(f"Added {src_path} to sys.path")

from app import app

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client