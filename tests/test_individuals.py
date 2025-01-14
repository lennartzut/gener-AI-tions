import pytest


def test_create_individual_unauthorized(client):
    """
    Test creating an individual without authorization.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 401 (Unauthorized).
    """
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "gender": "male",
        "birth_date": "1985-05-15",
        "death_date": None
    }
    resp = client.post("/api/individuals/?project_id=1",
                       json=payload)
    assert resp.status_code == 401


def test_create_individual_authorized(client):
    """
    Test creating an individual with valid credentials.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 201 (Created) and the response
        JSON contains the correct first name.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "gender": "female",
        "birth_date": "1985-05-15",
        "death_date": None
    }
    resp = client.post("/api/individuals/?project_id=1",
                       json=payload)
    assert resp.status_code == 201
    data = resp.json["data"]
    assert data["primary_identity"]["first_name"] == "Jane"


def test_individual_invalid_dates(client):
    """
    Test that birth_date cannot be after death_date.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 400 (Bad Request) and the
        appropriate error message is returned.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "gender": "male",
        "birth_date": "2025-01-01",
        "death_date": "2020-01-01"
    }
    resp = client.post("/api/individuals/?project_id=1",
                       json=payload)
    print(f"Raw Response: {resp.data.decode()}")
    print(f"Response Status Code: {resp.status_code}")
    print(f"Response Headers: {resp.headers}")
    assert resp.status_code == 400
    assert "Birth date must be before death date" in \
           resp.json["details"][0]["msg"]


def test_list_individuals(client):
    """
    Test listing individuals for a specific project.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 200 (OK) and the response JSON
        contains a list of individuals.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    resp = client.get("/api/individuals/?project_id=1")
    assert resp.status_code == 200
    assert "individuals" in resp.json
    assert isinstance(resp.json["individuals"], list)


def test_update_individual(client):
    """
    Test updating an individual's details.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        If response status code is 200 (OK), checks that the first
        name is updated.
        If status code is 404 (Not Found), no assertion is made.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    update_payload = {
        "first_name": "UpdatedFirstName",
        "birth_date": "1992-07-14"
    }
    resp = client.patch("/api/individuals/1?project_id=1",
                        json=update_payload)
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        updated_data = resp.json["data"]
        assert updated_data["primary_identity"][
                   "first_name"] == "UpdatedFirstName"


def test_delete_individual(client):
    """
    Test deleting an individual by ID.

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

    resp = client.delete("/api/individuals/1?project_id=1")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "message" in resp.json


def test_create_individual_invalid_data(client):
    """
    Test creating an individual with invalid data. The
    'first_name' can't be empty.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 400 (Bad Request) and that the
        appropriate validation error is present.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    invalid_payload = {
        "first_name": "",
        "last_name": "Doe",
        "gender": "male"
    }
    resp = client.post("/api/individuals/?project_id=1",
                       json=invalid_payload)
    assert resp.status_code == 400
    assert "error" in resp.json
    assert "details" in resp.json
    assert any(
        error.get(
            "type") == "string_too_short" and "first_name" in error.get(
            "loc", [])
        for error in resp.json.get("details", [])
    ), ("Expected 'string_too_short' error for 'first_name' not "
        "found in response details.")
