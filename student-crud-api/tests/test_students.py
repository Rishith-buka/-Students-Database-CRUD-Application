import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

os.environ["DATABASE_FILE"] = "students_test.db"

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    from app.database import get_connection, init_db

    init_db()
    with get_connection() as connection:
        connection.execute("DELETE FROM students")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'students'")
        connection.commit()
    yield


def test_create_student_success():
    payload = {
        "full_name": "Alice Johnson",
        "date_of_birth": "2005-02-15",
        "email": "alice@example.com",
        "phone": "9876543210",
        "course": "Computer Science",
        "address": "123 Main Street",
        "enrollment_date": "2024-08-01",
    }

    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Alice Johnson"
    assert data["student_id"] == 1
    assert data["email"] == "alice@example.com"


def test_list_students_with_filters():
    client.post(
        "/students",
        json={
            "full_name": "Alice Johnson",
            "date_of_birth": "2005-02-15",
            "email": "alice@example.com",
            "phone": "9876543210",
            "course": "Computer Science",
            "address": "123 Main Street",
            "enrollment_date": "2024-08-01",
        },
    )
    client.post(
        "/students",
        json={
            "full_name": "Bob Smith",
            "date_of_birth": "2004-08-10",
            "email": "bob@example.com",
            "phone": "9123456780",
            "course": "Mathematics",
        },
    )

    response = client.get("/students?name=alice&course=computer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Alice Johnson"

    dob_response = client.get("/students?date_of_birth=2004-08-10")
    assert dob_response.status_code == 200
    assert len(dob_response.json()) == 1
    assert dob_response.json()[0]["full_name"] == "Bob Smith"


def test_get_one_student_success():
    client.post(
        "/students",
        json={
            "full_name": "Charlie Brown",
            "date_of_birth": "2003-11-07",
            "email": "charlie@example.com",
            "phone": "9000000001",
            "course": "Physics",
        },
    )

    response = client.get("/students/1")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Charlie Brown"
    assert data["student_id"] == 1


def test_update_student_success():
    client.post(
        "/students",
        json={
            "full_name": "David Miller",
            "date_of_birth": "2002-04-20",
            "email": "david@example.com",
            "phone": "9712345678",
            "course": "History",
        },
    )

    payload = {
        "full_name": "David Lee Miller",
        "date_of_birth": "2002-04-20",
        "email": "david.new@example.com",
        "phone": "9712345679",
        "course": "History",
        "address": "77 Hill Road",
        "enrollment_date": "2023-09-10",
    }

    response = client.put("/students/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "David Lee Miller"
    assert data["email"] == "david.new@example.com"


def test_patch_student_success():
    client.post(
        "/students",
        json={
            "full_name": "Emma Davis",
            "date_of_birth": "2006-07-09",
            "email": "emma@example.com",
            "phone": "9988776655",
            "course": "Biology",
        },
    )

    response = client.patch("/students/1", json={"course": "Chemistry", "address": "8 Park Avenue"})
    assert response.status_code == 200
    data = response.json()
    assert data["course"] == "Chemistry"
    assert data["address"] == "8 Park Avenue"


def test_delete_student_success():
    client.post(
        "/students",
        json={
            "full_name": "Frank White",
            "date_of_birth": "2001-12-31",
            "email": "frank@example.com",
            "phone": "9300000000",
            "course": "Economics",
        },
    )

    response = client.delete("/students/1")
    assert response.status_code == 204

    get_response = client.get("/students/1")
    assert get_response.status_code == 404


def test_invalid_input_rejected():
    payload = {
        "full_name": "",
        "date_of_birth": "2005-02-15",
        "email": "invalid-email",
        "phone": "123",
    }

    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_duplicate_email_rejected():
    first = {
        "full_name": "Grace Miller",
        "date_of_birth": "2005-01-11",
        "email": "grace@example.com",
        "phone": "9123451234",
    }
    second = {
        "full_name": "Grace Duplicate",
        "date_of_birth": "2005-01-12",
        "email": "grace@example.com",
        "phone": "9123455678",
    }

    response_one = client.post("/students", json=first)
    assert response_one.status_code == 201

    response_two = client.post("/students", json=second)
    assert response_two.status_code == 409
    assert "already exists" in response_two.json()["detail"].lower()


def test_student_not_found_for_get_update_patch_delete():
    assert client.get("/students/999").status_code == 404
    assert client.put("/students/999", json={
        "full_name": "Ghost Student",
        "date_of_birth": "2000-01-01",
        "email": "ghost@example.com",
        "phone": "9999999999",
    }).status_code == 404
    assert client.patch("/students/999", json={"course": "Unknown"}).status_code == 404
    assert client.delete("/students/999").status_code == 404


def test_missing_contact_information_rejected():
    payload = {
        "full_name": "No Contact",
        "date_of_birth": "2001-05-10",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
