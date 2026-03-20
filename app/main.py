from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers_auth import router as auth_router

app = FastAPI(
    title="KumbhSetu API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}