import pytest

def test_get_user_profile_unauthorized(client):
    """
    Test retrieving user profile without authorization.
    """
    resp = client.get("/api/users/")
    assert resp.status_code == 401


def test_get_user_profile_authorized(client):
    """
    Test retrieving user profile with valid credentials.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)
    resp = client.get("/api/users/")
    assert resp.status_code == 200
    assert "user" in resp.json


def test_update_user_profile(client):
    """
    Test updating the user's profile.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)
    update_payload = {"username": "new_username", "email": "new_email@example.com"}
    resp = client.patch("/api/users/", json=update_payload)
    assert resp.status_code in (200, 409)


def test_delete_user_account(client):
    """
    Test deleting a user account.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)
    resp = client.delete("/api/users/")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "Account deleted successfully." in resp.json["message"]