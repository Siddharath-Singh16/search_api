import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.sqlite import init_db, get_db
from src.core.rate_limiter import rate_limit_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    rate_limit_store.clear()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees")
    cursor.execute("""
        INSERT INTO employees (
            id, org_id, first_name, last_name,
            contact_email, contact_phone,
            department, position, location, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "emp-123", "org1", "Emp005", "Test", "test005@example.com",
        "+1234567890", "Engineering", "Developer", "Remote", "ACTIVE"
    ))
    conn.commit()
    conn.close()


def test_search_api_success():
    response = client.get("/search/employees", params={
        "org_id": "org1",
        "search": "Emp005",
        "page": 1,
        "limit": 10
    })

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    emp = data[0]
    assert emp["first_name"] == "Emp005"
    assert emp["last_name"] == "Test"
    assert emp["department"] == "Engineering"
    assert emp["position"] == "Developer"



def test_search_api_missing_org():
    response = client.get("/search/employees", params={
        "org_id": "invalid_org"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid organization ID"


def test_search_api_rate_limit_exceeded():
    for _ in range(20):
        response = client.get("/search/employees", params={"org_id": "org1"})
        assert response.status_code == 200

    response = client.get("/search/employees", params={"org_id": "org1"})
    assert response.status_code == 429
    assert "Rate limit" in response.json()["detail"]

def test_data_isolation_between_orgs():
    conn = get_db()
    cursor = conn.cursor()

    # Insert a second employee for another org
    cursor.execute("""
        INSERT INTO employees (
            id, org_id, first_name, last_name,
            contact_email, contact_phone,
            department, position, location, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "emp-999", "org2", "Intruder", "WrongOrg", "intruder@example.com",
        "+999999999", "Marketing", "Lead", "Onsite", "ACTIVE"
    ))
    conn.commit()
    conn.close()

    # Make a request as org1
    response = client.get("/search/employees", params={
        "org_id": "org1"
    })

    assert response.status_code == 200
    data = response.json()
    assert all(emp["first_name"] != "Intruder" for emp in data)
    assert all(emp["first_name"] == "Emp005" for emp in data)
