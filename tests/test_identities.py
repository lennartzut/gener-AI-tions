import pytest


def test_create_identity_unauthorized(client):
    """
    Test creating an identity without authorization.
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
    assert resp.status_code == 400
    assert "Valid from date cannot be after valid until date." in resp.json["error"]