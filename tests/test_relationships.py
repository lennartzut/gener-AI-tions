import pytest


def test_create_relationship_unauthorized(client):
    """
    Test creating a relationship without authorization.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 401 (Unauthorized).
    """
    payload = {
        "individual_id": 1,
        "related_id": 2,
        "initial_relationship": "partner",
        "union_date": "2020-05-20",
        "dissolution_date": None
    }
    resp = client.post("/api/relationships/?project_id=1",
                       json=payload)
    assert resp.status_code == 401


def test_create_relationship_authorized(client):
    """
    Test creating a relationship with valid credentials.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 201 (Created) and a success
        message is returned.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "individual_id": 1,
        "related_id": 3,
        "initial_relationship": "partner",
        "union_date": "2020-05-20",
        "dissolution_date": None
    }
    resp = client.post("/api/relationships/?project_id=1",
                       json=payload)
    assert resp.status_code == 201
    assert "Relationship created successfully" in resp.json[
        "message"]


def test_relationship_self_reference(client):
    """
    Test that a relationship cannot link an individual to themselves.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is 400 (Bad Request) and an
        appropriate error message is returned.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    payload = {
        "individual_id": 1,
        "related_id": 1,
        "initial_relationship": "partner"
    }
    resp = client.post("/api/relationships/?project_id=1",
                       json=payload)
    assert resp.status_code == 400
    assert "Failed to create relationship." in resp.json["error"]


def test_update_relationship(client):
    """
    Test updating an existing relationship.

    Args:
        client (fixture): Test client for making HTTP requests.

    Asserts:
        Response status code is either 200 (OK) or 404 (Not Found).
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    update_payload = {
        "initial_relationship": "parent"
    }
    resp = client.patch("/api/relationships/1?project_id=1",
                        json=update_payload)
    assert resp.status_code in (200, 404)


def test_delete_relationship(client):
    """
    Test deleting a relationship by ID.

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

    resp = client.delete("/api/relationships/1?project_id=1")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "Relationship deleted successfully." in resp.json[
            "message"]
