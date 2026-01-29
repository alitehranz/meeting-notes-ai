from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models.database import init_db
import os

app = FastAPI(title="AI Meeting Notes Analyzer", version="1.0.0")

# Enviroment-aware CORS configuration
ENVIRONMENT= os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Production: Only allow frontend domain
    allowed_origins = [
        "https://*.netlify.app"
    ]
else:
    # Development: Allow localhost for testing
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialise database
init_db()

# Include routes
app.include_router(router, prefix="/api", tags=['meetings'])

@app.get("/")
async def root():
    return {
        "message": "AI Meeting Notes Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "create_meeting": "POST /api/meetings",
            "get_meetings": "GET /api/meetings",
            "get_meeting": "GET /api/meetings/{id}",
            "get_action_items": "GET /api/action-items"
        }

    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)