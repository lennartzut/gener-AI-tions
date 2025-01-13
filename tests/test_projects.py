import pytest


def test_list_projects_unauthorized(client):
    """
    Test listing projects without authorization.
    """
    resp = client.get("/api/projects/")
    assert resp.status_code == 401


def test_create_project_and_list(client):
    """
    Test creating a project and then listing all projects.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    # Create project
    create_payload = {"name": "My Test Project"}
    resp = client.post("/api/projects/", json=create_payload)
    assert resp.status_code == 201
    assert "Project created successfully." in resp.json["message"]

    # List projects
    list_resp = client.get("/api/projects/")
    assert list_resp.status_code == 200
    assert "projects" in list_resp.json
    assert any(proj["name"] == "My Test Project" for proj in
               list_resp.json["projects"])


def test_update_project(client):
    """
    Test updating an existing project.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    update_payload = {"name": "Updated Project Name"}
    resp = client.put("/api/projects/1", json=update_payload)
    assert resp.status_code in (200, 404)


def test_delete_project(client):
    """
    Test deleting a project by ID.
    """
    login_payload = {"email": "testuser@example.com",
                     "password": "TestPass123!"}
    client.post("/api/auth/login", json=login_payload)

    resp = client.delete("/api/projects/1")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "Project deleted successfully." in resp.json[
            "message"]
