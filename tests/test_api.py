import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.db.base import Base
from src.db.session import get_db
from src.models.employee import Employee
from src.core.rate_limiter import rate_limiter

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency for testing
@pytest.fixture(scope="function", autouse=True)
def override_get_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db
    rate_limiter.reset()

    employee = Employee(
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
    )
    db.add(employee)
    db.commit()
    yield
    db.close()

client = TestClient(app)

def test_search_api_success():
    response = client.get("/search/employees", params={
        "org_id": "org1",
        "search": "Test",
        "status": "active",
        "page": 1,
        "limit": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["first_name"] == "Test"

def test_invalid_org():
    response = client.get("/search/employees", params={"org_id": "invalid"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid organization ID"

def test_rate_limit_exceeded():
    for _ in range(20):
        response = client.get("/search/employees", params={"org_id": "org1"})
        assert response.status_code == 200

    # 21st request should fail
    response = client.get("/search/employees", params={"org_id": "org1"})
    assert response.status_code == 429
    assert "Rate limit" in response.json()["detail"]
