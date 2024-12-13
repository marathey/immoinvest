from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import hvac




app = FastAPI(title="Your App Name")



@app.get("/")
async def read_root():

    client = hvac.Client(
        url='http://vault:8200',
        token=''  # Use appropriate authentication method in production
    )

    # Read the secret
    secret = client.secrets.kv.v2.read_secret_version(
        path='database/config',
        mount_point="secret"
    )
    return {"message": secret}
    #return {"message": "hello"}

