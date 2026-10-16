from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    original_activities = deepcopy(app_module.activities)
    try:
        with TestClient(app_module.app) as test_client:
            yield test_client
    finally:
        app_module.activities.clear()
        app_module.activities.update(original_activities)


def test_get_activities_returns_activity_details_and_participants(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    activity_name = "Basketball Team"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Basketball Team"
    email = "new.student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    assert client.post(signup_url, params={"email": email}).status_code == 200
    response = client.post(signup_url, params={"email": email})

    assert response.status_code == 400
    assert client.get("/activities").json()[activity_name]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_rejects_unknown_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "not.signed.up@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404