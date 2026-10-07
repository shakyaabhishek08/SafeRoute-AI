from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Routers
from app.routes.auth_routes import router as auth_router
from app.routes.incident_routes import router as incident_router
from app.routes.route_routes import router as route_router
from app.routes.chatbot_routes import router as chatbot_router
from app.routes.chat_history import router as chat_history_router
from app.routes.admin_routes import router as admin_router


# -------------------------------------------------------
# FastAPI Application
# -------------------------------------------------------

app = FastAPI(
    title="SafeRoute AI",
    version="1.0.0",
    description="AI Powered Safe Navigation System"
)


# -------------------------------------------------------
# CORS
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Include Routers
# -------------------------------------------------------

app.include_router(
    auth_router,
    tags=["Authentication"]
)

app.include_router(
    incident_router,
    tags=["Incidents"]
)

app.include_router(
    route_router,
    tags=["Routes"]
)

app.include_router(
    chatbot_router,
    tags=["Chatbot"]
)

app.include_router(
    chat_history_router,
    tags=["Chat History"]
)

app.include_router(
    admin_router,
    tags=["Admin"]
)


# -------------------------------------------------------
# Root
# -------------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "SafeRoute AI Backend Running"
    }


# -------------------------------------------------------
# API Status
# -------------------------------------------------------

@app.get("/api")
async def api_status():
    return {
        "service": "SafeRoute AI",
        "status": "running",
        "version": "1.0.0"
    }


# -------------------------------------------------------
# Health Check
# -------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "SafeRoute AI"
    }