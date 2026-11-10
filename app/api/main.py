
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import projects, history, executions

# Initialize FastAPI application
app = FastAPI(
    title="TestPilot AI API",
    description="AI-powered Test Automation and Repair Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://frontend-2cik.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(projects.router)
app.include_router(history.router)
app.include_router(executions.router)


@app.get("/")
def root():
    return {
        "message": "TestPilot AI Backend is running"
    }
