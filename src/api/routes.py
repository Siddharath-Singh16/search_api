from fastapi import APIRouter
from src.api.endpoints import employee

api_router = APIRouter()
api_router.include_router(employee.router, prefix="/employees", tags=["Employees"])