import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_available_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert isinstance(payload[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Swim Club"
    email = "new_student@example.com"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Drama Club"
    email = "duplicate_student@example.com"
    url = f"/activities/{activity_name}/signup"
    client.post(url, params={"email": email})

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = "withdrawn_student@example.com"
    signup_url = f"/activities/{activity_name}/signup"
    client.post(signup_url, params={"email": email})
    remove_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(remove_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "missing_student@example.com"
    remove_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(remove_url, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
