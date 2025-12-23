from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional

app = FastAPI(title="Memory Service", description="A proxy service that forwards requests to memory_logic")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URL
MEMORY_LOGIC_URL = "http://memory_logic:8000"

# Pydantic models to match memory_logic
class CreateGameRequest(BaseModel):
    userId: int
    size: int

class FlipCardRequest(BaseModel):
    game_id: int
    local_id: int

@app.get("/")
async def root():
    return {"message": "Memory Service is running"}

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MEMORY_LOGIC_URL}/health")
            if response.status_code == 200:
                return {"status": "healthy", "memory_logic": "connected"}
            else:
                return {"status": "unhealthy", "memory_logic": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "memory_logic": "disconnected", "error": str(e)}

@app.post("/create_game")
async def create_game(request: CreateGameRequest):
    """
    Forwards create_game request to memory_logic service
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MEMORY_LOGIC_URL}/create_game",
                json=request.model_dump()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create game: {response.text}"
                )
            
            return response.json()
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory_logic service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.post("/flip_card")
async def flip_card(request: FlipCardRequest):
    """
    Forwards flip_card request to memory_logic service
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MEMORY_LOGIC_URL}/flip_card",
                json=request.model_dump()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to flip card: {response.text}"
                )
            
            return response.json()
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory_logic service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/game_status/{game_id}")
async def get_game_status(game_id: int):
    """
    Forwards game_status request to memory_logic service
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MEMORY_LOGIC_URL}/game_status/{game_id}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get game status: {response.text}"
                )
            
            return response.json()
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory_logic service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)