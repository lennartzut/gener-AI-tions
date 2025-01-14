import pytest


def test_get_user_profile_unauthorized(client):
    """
    Test retrieving user profile without authorization.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 401 (Unauthorized).
    """
    resp = client.get("/api/users/")
    assert resp.status_code == 401


def test_get_user_profile_authorized(client):
    """
    Test retrieving user profile with valid credentials.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 200 (OK) and 'user' is present in
        the response JSON.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    resp = client.get("/api/users/")
    assert resp.status_code == 200
    assert "user" in resp.json


def test_update_user_profile(client):
    """
    Test updating the user's profile.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is either 200 (OK) or 409 (Conflict).
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    update_payload = {
        "username": "new_username",
        "email": "new_email@example.com"
    }
    resp = client.patch("/api/users/", json=update_payload)
    assert resp.status_code in (200, 409)


def test_delete_user_account(client):
    """
    Test deleting a user account.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        If response status code is 200 (OK), checks for a success
        message in the response JSON.
        If status code is 404 (Not Found), no assertion is made.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    resp = client.delete("/api/users/")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "Account deleted successfully." in resp.json[
            "message"]
