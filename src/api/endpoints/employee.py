from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional
from src.schemas.employee_schema import EmployeeOut
from src.services.employee_service import search_employees
from src.db.session import get_db
from src.core.rate_limiter import rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/employees")
async def search(
    request: Request,
    org_id: str = Query(...),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for employees within an organization with filtering options.
    
    Args:
        request: FastAPI request object
        org_id: Organization ID to filter by
        search: Optional search term for name, department, or position
        status: Optional status filter
        page: Page number (1-indexed)
        limit: Number of results per page
        db: Database session
        
    Returns:
        List of employee records filtered by organization configuration
    """
    try:
        # Log request for monitoring
        logger.info(f"Search request: org_id={org_id}, search={search}, status={status}, page={page}, limit={limit}, ip={request.client.host}")
        
        # Enforce rate limit
        try:
            rate_limiter.enforce(org_id)
        except HTTPException as e:
            logger.warning(f"Rate limit exceeded for org_id={org_id}, ip={request.client.host}")
            raise e
        
        # Validate organization
        if not is_valid_org(org_id):
            logger.warning(f"Invalid organization ID: {org_id}, ip={request.client.host}")
            raise HTTPException(status_code=400, detail="Invalid organization ID")
        
        # Execute search
        result = search_employees(db, org_id, search, status, page, limit)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise
    except SQLAlchemyError as e:
        # Log database errors but don't expose details to client
        logger.error(f"Database error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

def is_valid_org(org_id: str) -> bool:
    """
    Validate if the organization ID exists.
    
    Args:
        org_id: Organization ID to validate
        
    Returns:
        Boolean indicating if the organization is valid
    """
    # basic mock org check
    return org_id in ["org1", "org2"]