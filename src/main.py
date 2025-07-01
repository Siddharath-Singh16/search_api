from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import api_router
from src.middleware.rate_limiter import RateLimiterMiddleware
from src.config import settings
from src.db.session import get_db
from src.db.seed import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        db = next(get_db())
        seed_data(db)
    
    yield
    

app = FastAPI(title="Employee Search API", lifespan=lifespan)

app.add_middleware(
    RateLimiterMiddleware,
    rate_limit=20,
    window_seconds=60
)

app.include_router(api_router)