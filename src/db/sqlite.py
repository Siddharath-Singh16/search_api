import sqlite3
import uuid
import random
import os


DB_PATH = "hr.db"

def get_db():
    db_path = os.getenv("DB_PATH", "hr.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            org_id TEXT,
            first_name TEXT,
            last_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            department TEXT,
            position TEXT,
            location TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def seed_mock_data(n=100):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] > 0:
        return

    departments = ["Engineering", "Sales", "HR", "Design"]
    positions = ["Manager", "Developer", "Executive", "Designer"]
    locations = ["New York", "San Francisco", "Remote"]
    statuses = ["ACTIVE", "NOT_STARTED", "TERMINATED"]

    for _ in range(n):
        emp = (
            str(uuid.uuid4()),
            random.choice(["org1", "org2"]),
            f"John{random.randint(1,1000)}",
            f"Doe{random.randint(1,1000)}",
            f"john{random.randint(1,1000)}@example.com",
            f"+1234567890",
            random.choice(departments),
            random.choice(positions),
            random.choice(locations),
            random.choice(statuses),
        )
        cursor.execute("""
            INSERT INTO employees (
                id, org_id, first_name, last_name,
                contact_email, contact_phone,
                department, position, location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, emp)

    conn.commit()
    conn.close()

