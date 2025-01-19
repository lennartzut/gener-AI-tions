import pytest

def test_create_individual_unauthorized(client):
    """
    Test creating an individual without authorization.
    """
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "gender": "male",
        "birth_date": "1985-05-15",
        "death_date": None
    }
    resp = client.post("/api/individuals/?project_id=1", json=payload)
    assert resp.status_code == 401


def test_create_individual_authorized(client):
    """
    Test creating an individual with valid credentials.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "gender": "female",
        "birth_date": "1985-05-15",
        "death_date": None
    }
    resp = client.post("/api/individuals/?project_id=1", json=payload)
    assert resp.status_code == 201
    data = resp.json["individual"]
    # your new code may store the name under data["primary_identity"]["first_name"]
    # if so, keep as is:
    assert data["primary_identity"]["first_name"] == "Jane"


def test_individual_invalid_dates(client):
    """
    Test that birth_date cannot be after death_date.
    Expects 400 with the new code.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "gender": "male",
        "birth_date": "2025-01-01",
        "death_date": "2020-01-01"
    }
    resp = client.post("/api/individuals/?project_id=1", json=payload)
    assert resp.status_code == 400

    # If new code returns details
    if "details" in resp.json:
        assert "Birth date must be before death date" in resp.json["details"][0]["msg"]
    else:
        # otherwise, check main error
        assert "Birth date must be before death date" in resp.json["error"]


def test_list_individuals(client):
    """
    Test listing individuals for a specific project.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)
    resp = client.get("/api/individuals/?project_id=1")
    assert resp.status_code == 200
    assert "individuals" in resp.json
    assert isinstance(resp.json["individuals"], list)


def test_update_individual(client):
    """
    Test updating an individual's details.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    update_payload = {
        "first_name": "UpdatedFirstName",
        "birth_date": "1992-07-14"
    }
    resp = client.patch("/api/individuals/1?project_id=1", json=update_payload)
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        updated_data = resp.json["data"]
        assert updated_data["primary_identity"]["first_name"] == "UpdatedFirstName"


def test_delete_individual(client):
    """
    Test deleting an individual by ID.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)
    resp = client.delete("/api/individuals/1?project_id=1")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "message" in resp.json


def test_create_individual_invalid_data(client):
    """
    Test creating an individual with invalid data. The 'first_name' can't be empty.
    """
    login_payload = {"email": "testuser@example.com", "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    invalid_payload = {
        "first_name": "",
        "last_name": "Doe",
        "gender": "male"
    }
    resp = client.post("/api/individuals/?project_id=1", json=invalid_payload)
    assert resp.status_code == 400
    assert "error" in resp.json

    # If your new code always re-raises ValidationError => it includes "details"
    if "details" in resp.json:
        assert any(
            err.get("type") == "string_too_short" and "first_name" in err.get("loc", [])
            for err in resp.json["details"]
        ), "Expected 'string_too_short' for 'first_name' not found."