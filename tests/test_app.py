import copy

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


client = TestClient(app)


def setup_function():
    reset_activities()


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert "Chess Club" in body
    assert "Programming Class" in body
    assert body["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test_user@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test_user@mergington.edu for Chess Club"
    assert "test_user@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    email = "remove_me@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")

    response = client.delete(f"/activities/Chess%20Club/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants/missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
