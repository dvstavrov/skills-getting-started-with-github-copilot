import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Test GET /activities

def test_get_activities():
    # Arrange: (No setup needed for this test)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all("description" in v and "schedule" in v and "participants" in v and "max_participants" in v for v in data.values())

# Test POST /activities/{activity}/signup

def test_signup_participant():
    # Arrange
    activity = next(iter(client.get("/activities").json().keys()))
    email = "testuser@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code in (200, 201)
    data = response.json()
    assert "message" in data or "detail" in data
    # Clean up: Remove participant if added
    client.delete(f"/activities/{activity}/signup?email={email}")

# Test DELETE /activities/{activity}/signup

def test_delete_participant():
    # Arrange
    activity = next(iter(client.get("/activities").json().keys()))
    email = "deleteuser@mergington.edu"
    # Ensure participant is signed up first
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code in (200, 204)
    # Confirm participant is removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

# Edge case: duplicate signup

def test_duplicate_signup():
    # Arrange
    activity = next(iter(client.get("/activities").json().keys()))
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code >= 400
    # Clean up
    client.delete(f"/activities/{activity}/signup?email={email}")

# Edge case: invalid email

def test_invalid_email():
    # Arrange
    activity = next(iter(client.get("/activities").json().keys()))
    email = "notanemail"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code >= 400
