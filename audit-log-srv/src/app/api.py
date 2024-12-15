from fastapi import FastAPI
from app.routes import router
from app.database import setup_db

# Initialize FastAPI app
app = FastAPI()

# Include router
app.include_router(router)

# Database setup
@app.on_event("startup")
async def on_startup():
    await setup_db()
