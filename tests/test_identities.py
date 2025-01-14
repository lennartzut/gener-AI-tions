import pytest


def test_create_identity_unauthorized(client):
    """
    Test creating an identity without authorization.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 401 (Unauthorized).
    """
    payload = {
        "individual_id": 1,
        "first_name": "Alias",
        "last_name": "Example",
        "gender": "male",
        "valid_from": "2020-01-01",
        "valid_until": None
    }
    resp = client.post("/api/identities/?project_id=1", json=payload)
    assert resp.status_code == 401


def test_create_identity_authorized(client):
    """
    Test creating an identity with valid credentials.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 201 (Created) and a success
        message is returned.
    """
    login_payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "individual_id": 1,
        "first_name": "Alternate",
        "last_name": "Identity",
        "gender": "unknown",
        "valid_from": "2020-01-01",
        "valid_until": "2025-01-01"
    }
    resp = client.post("/api/identities/?project_id=1", json=payload)
    assert resp.status_code == 201
    assert "Identity created successfully" in resp.json["message"]


def test_identity_invalid_date_range(client):
    """
    Test creating an identity with an invalid date range.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 400 (Bad Request) and an
        appropriate error message is returned.
    """
    login_payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "individual_id": 1,
        "first_name": "Alias",
        "last_name": "Example",
        "gender": "male",
        "valid_from": "2025-01-01",
        "valid_until": "2020-01-01"
    }
    resp = client.post("/api/identities/?project_id=1", json=payload)
    print(f"Raw Response: {resp.data.decode()}")
    print(f"Response Status Code: {resp.status_code}")
    print(f"Response Headers: {resp.headers}")
    assert resp.status_code == 400
    assert "Valid from date cannot be after valid until date" in \
           resp.json["details"][0]["msg"]
