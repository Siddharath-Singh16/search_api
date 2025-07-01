from pydantic import BaseModel

class EmployeeOut(BaseModel):
    first_name: str
    last_name: str
    department: str
    position: str
    contact_email: str | None = None
    contact_phone: str | None = None
    location: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True
