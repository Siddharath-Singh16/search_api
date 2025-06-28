from fastapi import APIRouter, Query, HTTPException
from src.core.config import ORG_DISPLAY_CONFIG
from src.core.rate_limiter import enforce_rate_limit
from src.db.sqlite import get_db

router = APIRouter()

@router.get("/employees")
def search_employees(
    org_id: str = Query(...),
    search: str = Query(""),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
):
    enforce_rate_limit(org_id)

    display_columns = ORG_DISPLAY_CONFIG.get(org_id)
    if not display_columns:
        raise HTTPException(status_code=400, detail="Invalid organization ID")

    conn = get_db()
    cursor = conn.cursor()

    query = f"SELECT {', '.join(display_columns)} FROM employees WHERE org_id = ?"
    params = [org_id]

    if search:
        like = f"%{search}%"
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR department LIKE ? OR position LIKE ? OR location LIKE ?)"
        params.extend([like] * 5)

    if status:
        status = status.upper()
        query += " AND UPPER(status) = ?"
        params.append(status)

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, (page - 1) * limit])

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]
