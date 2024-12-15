from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-testing")
ALGORITHM = "HS256"

class AuthenticationError(Exception):
    pass

def create_test_token(user_id: str = "test-user"):
    """Create a test token - for development only"""
    data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validate JWT token and return user information"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise AuthenticationError("Could not validate credentials")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )