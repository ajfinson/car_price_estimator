from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes import router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Car Lifetime TCO API",
    description="Calculate the total cost of ownership for a vehicle over its lifetime",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Car Lifetime TCO API",
        "version": "1.0.0",
        "endpoints": {
            "estimate": "POST /api/tco/estimate"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
