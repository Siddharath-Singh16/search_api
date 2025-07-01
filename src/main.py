from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import api_router
from src.core.rate_limiter import rate_limiter
from src.config import settings
from src.db.session import get_db
from src.db.seed import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        db = next(get_db())
        seed_data(db)
    
    yield
    
    # Shutdown logic
    rate_limiter.cleanup()

app = FastAPI(title="Employee Search API", lifespan=lifespan)

app.include_router(api_router)