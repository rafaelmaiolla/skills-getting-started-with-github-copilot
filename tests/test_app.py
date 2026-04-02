import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Arrange — no extra state needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_activities_contains_expected_keys():
    # Arrange — no extra state needed

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_already_registered():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already in seed data

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "x@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already in seed data

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "x@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_found():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


# ---------------------------------------------------------------------------
# GET / (redirect)
# ---------------------------------------------------------------------------

def test_root_redirects_to_static():
    # Arrange
    no_follow_client = TestClient(app, follow_redirects=False)

    # Act
    response = no_follow_client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
