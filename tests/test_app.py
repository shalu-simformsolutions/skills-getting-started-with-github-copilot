import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Fixture to reset activities before each test (if needed)
@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities dict if needed
    # If src.app exposes activities, reset here
    try:
        from src.app import activities
        for activity in activities.values():
            activity['participants'] = []
    except ImportError:
        pass
    yield


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Soccer Club" in data
    assert "Basketball Team" in data


def test_signup_success():
    payload = {"email": "alice@example.com"}
    response = client.post("/activities/Soccer Club/signup", params=payload)
    assert response.status_code == 200
    assert "Signed up alice@example.com for Soccer Club" in response.json()["message"]


def test_signup_activity_not_found():
    payload = {"email": "bob@example.com"}
    response = client.post("/activities/Unknown Activity/signup", params=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate():
    payload = {"email": "charlie@example.com"}
    # First signup
    response1 = client.post("/activities/Basketball Team/signup", params=payload)
    assert response1.status_code == 200
    # Duplicate signup
    response2 = client.post("/activities/Basketball Team/signup", params=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student already signed up"


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    # Should redirect (307 or 302)
    assert response.status_code in (302, 307)
    assert "/static/index.html" in response.headers["location"]
