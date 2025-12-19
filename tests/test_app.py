from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of initial activities to restore after each test
    import copy

    original = {
        name: {
            "description": details.get("description"),
            "schedule": details.get("schedule"),
            "max_participants": details.get("max_participants"),
            "participants": list(details.get("participants", [])),
        }
        for name, details in activities.items()
    }

    yield

    # Restore original state
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Programming Class" in data


def test_signup_and_unregister_flow():
    activity = "Programming Class"
    email = "newstudent@mergington.edu"

    # Ensure email not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Verify present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_duplicate_fails():
    activity = "Programming Class"
    # Use an existing participant from fixtures
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent_fails():
    activity = "Programming Class"
    email = "doesnotexist@mergington.edu"

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404
