import os
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from orchestrator import run_parallel_investigation

app = FastAPI(
    title="Core-OSINT Stateless Engine",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

X_OSINT_KEY = os.getenv("X-OSINT-KEY")
if not X_OSINT_KEY:
    raise RuntimeError("CRITICAL ERROR: 'X-OSINT-KEY' environment variable is unassigned.")

class InvestigationRequest(BaseModel):
    target: str = Field(..., description="The query identifier string (Email or Username)")
    type: str = Field(..., description="The scoping category constraint")

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        normalized = value.lower().strip()
        if normalized not in ["username", "email"]:
            raise ValueError("Type flag constraint invalid. Must select 'username' or 'email'.")
        return normalized

@app.post("/api/v1/investigate")
async def investigate(
    payload: InvestigationRequest,
    x_osint_key: str = Header(None, alias="X-OSINT-KEY")
):
    if not x_osint_key or x_osint_key != X_OSINT_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security Authentication Failed - Invalid Token Footprint."
        )
    
    try:
        results = await run_parallel_investigation(payload.target, payload.type)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Downstream Orchestration Crash: {str(e)}"
        )
      
