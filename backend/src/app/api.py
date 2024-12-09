from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Your App Name")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}