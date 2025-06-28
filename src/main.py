from fastapi import FastAPI
from src.api.routes import router as employee_router
from src.db.sqlite import init_db, seed_mock_data
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_mock_data()
    yield

app = FastAPI(title="Employee Search API", lifespan=lifespan)

app.include_router(employee_router, prefix="/search")
