import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db.base import Base
from src.db.session import get_db
from src.models.employee import Employee

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def override_get_db():
    """Setup test database with sample data before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db

    # Add test employees
    employees = [
        Employee(
            id="emp-123",
            org_id="org1",
            first_name="Test",
            last_name="User",
            contact_email="test@example.com",
            contact_phone="+1111111111",
            department="Engineering",
            position="Developer",
            location="Remote",
            status="ACTIVE"
        ),
        Employee(
            id="emp-124",
            org_id="org1",
            first_name="Jane",
            last_name="Smith",
            contact_email="jane@example.com",
            contact_phone="+2222222222",
            department="Marketing",
            position="Manager",
            location="New York",
            status="ACTIVE"
        ),
        Employee(
            id="emp-125",
            org_id="org1",
            first_name="John",
            last_name="Doe",
            contact_email="john@example.com",
            contact_phone="+3333333333",
            department="Engineering",
            position="Senior Developer",
            location="Remote",
            status="INACTIVE"
        ),
        Employee(
            id="emp-126",
            org_id="org2",
            first_name="Bob",
            last_name="Johnson",
            contact_email="bob@example.com",
            contact_phone="+4444444444",
            department="HR",
            position="Specialist",
            location="Chicago",
            status="ACTIVE"
        )
    ]
    
    for employee in employees:
        db.add(employee)
    
    db.commit()
    yield
    db.close()
    app.dependency_overrides.clear()


def test_search_api_success():
    """Test basic employee search with valid org_id"""
    response = client.get("/employees/search", params={
        "org_id": "org1",
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # All 3 employees from org1
    assert {emp["first_name"] for emp in data} == {"Test", "Jane", "John"}


def test_search_with_text_filter():
    """Test employee search with text filter"""
    response = client.get("/employees/search", params={
        "org_id": "org1",
        "search": "Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Test"


def test_search_with_status_filter():
    """Test employee search with status filter"""
    response = client.get("/employees/search", params={
        "org_id": "org2",
        "status": "ACTIVE"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert all(emp["status"] == "ACTIVE" for emp in data)


def test_search_with_pagination():
    """Test employee search with pagination"""
    # Get first page with 2 results per page
    response = client.get("/employees/search", params={
        "org_id": "org1",
        "page": 1,
        "limit": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Get second page with 2 results per page
    response = client.get("/employees/search", params={
        "org_id": "org1",
        "page": 2,
        "limit": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_search_different_org():
    """Test employee search for different organization"""
    response = client.get("/employees/search", params={
        "org_id": "org2",
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Bob"


def test_invalid_org_id():
    """Test that invalid org_id returns 400"""
    response = client.get("/employees/search", params={"org_id": "invalid-org"})
    assert response.status_code == 400
    assert "Invalid organization ID" in response.json()["detail"]


def test_search_no_results():
    """Test search with no matching results"""
    response = client.get("/employees/search", params={
        "org_id": "org1",
        "search": "NonexistentName"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0