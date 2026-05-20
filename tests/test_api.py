"""
Basic API endpoint tests for KumbhSetu Chatbot.

These tests verify that core API routes are working correctly
and returning expected responses.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_health_endpoint(client):
    """
    Test the /health endpoint returns 200 status.
    
    The health endpoint is crucial for deployment verification.
    It's used by Docker health checks and load balancers.
    
    Args:
        client: FastAPI TestClient fixture
    """
    response = client.get("/health")
    
    # Verify the response status code
    assert response.status_code == 200
    
    # Verify the response JSON structure
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


@pytest.mark.api
def test_root_endpoint(client):
    """
    Test the root endpoint returns appropriate response.
    
    Args:
        client: FastAPI TestClient fixture
    """
    response = client.get("/")
    
    # Root endpoint may not exist, but we document expected behavior
    # If it does exist, it should return a valid HTTP response
    assert response.status_code in [200, 404, 405]


@pytest.mark.api
def test_health_response_structure(client):
    """
    Test that health endpoint response has correct structure.
    
    This ensures the monitoring systems can rely on consistent
    response format from the health check endpoint.
    
    Args:
        client: FastAPI TestClient fixture
    """
    response = client.get("/health")
    assert response.status_code == 200
    
    json_data = response.json()
    # Must have status field
    assert isinstance(json_data, dict)
    assert "status" in json_data
