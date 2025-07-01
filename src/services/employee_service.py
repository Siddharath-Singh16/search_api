from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import List, Dict, Any, Optional
from src.models.employee import Employee
from src.schemas.employee_schema import EmployeeOut
from src.org_config.column_config import ORG_COLUMN_CONFIG
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def search_employees(
    db: Session, 
    org_id: str, 
    search: Optional[str] = None, 
    status: Optional[str] = None, 
    page: int = 1, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for employees based on provided filters.
    
    Args:
        db: Database session
        org_id: Organization ID to filter by
        search: Optional search term for name, department, or position
        status: Optional status filter
        page: Page number (1-indexed)
        limit: Number of results per page
        
    Returns:
        List of employee dictionaries with fields filtered by org configuration
        
    Raises:
        HTTPException: For database errors or invalid parameters
    """
    try:
        # Validate inputs
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        
        query = db.query(Employee).filter(Employee.org_id == org_id)
        
        if status:
            query = query.filter(Employee.status.ilike(status))
        
        if search and len(search) <= 100:  # Limit search length
            pattern = f"%{search}%"
            query = query.filter(
                Employee.first_name.ilike(pattern) |
                Employee.last_name.ilike(pattern) |
                Employee.department.ilike(pattern) |
                Employee.position.ilike(pattern)
            )
        
  
        
        results = query.offset((page - 1) * limit).limit(limit).all()
        
        allowed_fields = ORG_COLUMN_CONFIG.get(org_id, [])
        if not allowed_fields:
            logger.warning(f"No column configuration found for org_id: {org_id}")
            allowed_fields = ["first_name", "last_name"]  # Fallback to basic fields
        
        return [
            EmployeeOut.model_validate(emp).model_dump(include=allowed_fields)
            for emp in results
        ]
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in search_employees: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error in search_employees: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")