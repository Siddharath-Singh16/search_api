from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from src.schemas.employee_schema import EmployeeOut
from src.services.employee_service import search_employees
from src.db.session import get_db
from src.core.rate_limiter import rate_limiter

router = APIRouter()

@router.get("/employees")
def search(
    org_id: str = Query(...),
    search: str = Query(""),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    rate_limiter.enforce(org_id)
    if not is_valid_org(org_id):
        raise HTTPException(status_code=400, detail="Invalid organization ID")
    result = search_employees(db, org_id, search, status, page, limit)
    return result

def is_valid_org(org_id: str) -> bool:
    # basic mock org check
    return org_id in ["org1", "org2"]