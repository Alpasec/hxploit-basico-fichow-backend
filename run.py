import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.BACKEND_PORT))
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=port,
        reload=settings.APP_ENV == "development",
    )
