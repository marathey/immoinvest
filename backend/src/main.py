import uvicorn
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.api import app

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"]
    )