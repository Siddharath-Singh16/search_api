from sqlalchemy import Column, String
from src.db.base import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    department = Column(String)
    position = Column(String)
    location = Column(String)
    status = Column(String)