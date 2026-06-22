from src import app as app_module


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")
    payload = response.json()

    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_success_adds_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_full_activity_returns_400(client):
    activity = app_module.activities["Basketball Team"]
    already_signed_up = len(activity["participants"])
    slots_to_fill = activity["max_participants"] - already_signed_up

    for index in range(slots_to_fill):
        activity["participants"].append(f"filled{index}@mergington.edu")

    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "latecomer@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_success_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "notfound@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"