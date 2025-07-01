import uuid
import random
from src.models.employee import Employee


def seed_data(db):
    if db.query(Employee).first():
        return

    departments = ["Engineering", "Sales", "HR", "Design"]
    positions = ["Manager", "Developer", "Executive", "Designer"]
    locations = ["New York", "San Francisco", "Remote"]
    statuses = ["ACTIVE", "NOT_STARTED", "TERMINATED"]

    for i in range(50):
        emp = Employee(
            id=str(uuid.uuid4()),
            org_id=random.choice(["org1", "org2"]),
            first_name=f"John{i}",
            last_name="Doe",
            contact_email=f"john{i}@example.com",
            contact_phone="+1234567890",
            department=random.choice(departments),
            position=random.choice(positions),
            location=random.choice(locations),
            status=random.choice(statuses),
        )
        db.add(emp)
    db.commit()