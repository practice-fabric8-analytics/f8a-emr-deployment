"""Unit tests for the REST API module"""

import json


def get_json_from_response(response):
    """Decode JSON from response."""
    return json.loads(response.data.decode('utf8'))


def test_heart_beat_endpoint(client):
    """Test the heart beat endpoint."""
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    json_data = get_json_from_response(response)
    assert "status" in json_data
    assert json_data["status"] == "ok"