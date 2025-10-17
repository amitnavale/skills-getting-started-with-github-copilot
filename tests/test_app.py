import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code in [200, 307]  # Either direct response or redirect
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Test that we get a dictionary of activities
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "test@mergington.edu" in response.json()["message"]

    # Test duplicate signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

    # Test signup for non-existent activity
    response = client.post("/activities/NonExistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    # First sign up a test user
    email = "testunregister@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Test successful unregistration
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert email in response.json()["message"]
    assert "unregistered" in response.json()["message"].lower()

    # Test unregister when not registered
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

    # Test unregister from non-existent activity
    response = client.delete("/activities/NonExistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()