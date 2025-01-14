import pytest


def test_signup_success(client):
    """
    Test successful user signup.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 201 (Created) and a success
        message is returned.
    """
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123!",
        "confirm_password": "NewPass123!"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    assert "Signup successful!" in resp.json["message"]


def test_signup_conflict(client):
    """
    Test signup conflict with existing username or email.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 409 (Conflict) and an appropriate
        error message is returned.
    """
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Pass12345",
        "confirm_password": "Pass12345"
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "Email or username already in use." in resp.json["error"]


def test_login_success(client):
    """
    Test successful user login.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 200 (OK) and a success message is
        returned.
    """
    payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    resp = client.post("/api/auth/login", json=payload)
    assert resp.status_code == 200
    assert "Login successful!" in resp.json["message"]


def test_login_failure_wrong_password(client):
    """
    Test login failure due to incorrect password.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 401 (Unauthorized) and an
        appropriate error message is returned.
    """
    payload = {
        "email": "testuser@example.com",
        "password": "WrongPassword"
    }
    resp = client.post("/api/auth/login", json=payload)
    assert resp.status_code == 401
    assert "Invalid email or password." in resp.json["error"]


def test_logout(client):
    """
    Test logging out a user.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 200 (OK) and a success message is
        returned.
    """
    payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    client.post("/api/auth/login", json=payload)
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert "Logged out successfully." in logout_resp.json["message"]
