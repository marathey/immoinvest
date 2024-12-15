from fastapi import FastAPI
from app.routes.company_routes import router as company_router
from app.routes.company_status_routes import router as company_status_router
from app.database import setup_db

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(company_router)
app.include_router(company_status_router)

# Database setup
@app.on_event("startup")
async def on_startup():
    await setup_db()