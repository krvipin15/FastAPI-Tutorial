from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, posts, users, votes

# Instantiate the FastAPI application
app: FastAPI = FastAPI()

# Configure CORS - pass the class first, then the configuration as kwargs
app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=["*"],  # Frontend URL (e.g., React, Vue)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Home page
@app.get("/")
def root() -> str:
    return "Home Page"


# Register API routers
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)
