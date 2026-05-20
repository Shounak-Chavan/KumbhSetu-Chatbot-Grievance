"""
Pytest configuration and fixtures for testing.

This module sets up common test fixtures used across test files,
including FastAPI TestClient and database fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Fixture providing a FastAPI TestClient instance.
    
    The TestClient allows us to test FastAPI endpoints without running
    a live server. It simulates HTTP requests to the application.
    
    Returns:
        TestClient: Configured test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def test_user():
    """
    Fixture providing a sample user object for tests.
    
    This represents a typical user in the system and can be used
    across multiple test cases.
    
    Returns:
        dict: Sample user data
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
