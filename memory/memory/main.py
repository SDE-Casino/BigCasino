from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

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

# JWT verification function
def verify_jwt_token(request: Request):
    """
    Verify JWT token from Authorization header
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    print(f"[MEMORY SERVICE] Verifying token: {jwt_token[:50]}...")  # DEBUG LOG
    print(f"[MEMORY SERVICE] JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')[:20]}...")  # DEBUG LOG
    print(f"[MEMORY SERVICE] JWT_ALGORITHM: {os.getenv('JWT_ALGORITHM')}")  # DEBUG LOG

    try:
        decoded = jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        print(f"[MEMORY SERVICE] Token decoded successfully: {decoded}")  # DEBUG LOG
        return decoded
    except jwt.ExpiredSignatureError as e:
        print(f"[MEMORY SERVICE] Token expired error: {e}")  # DEBUG LOG
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"[MEMORY SERVICE] Invalid token error: {e}")  # DEBUG LOG
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic models to match memory_logic
class CreateGameRequest(BaseModel):
    userId: str  # Changed to UUID string
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
async def create_game(request: Request, create_request: CreateGameRequest):
    """
    Forwards create_game request to memory_logic service
    """
    verify_jwt_token(request)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MEMORY_LOGIC_URL}/create_game",
                json=create_request.model_dump()
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
async def flip_card(request: Request, flip_request: FlipCardRequest):
    """
    Forwards flip_card request to memory_logic service
    """
    verify_jwt_token(request)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MEMORY_LOGIC_URL}/flip_card",
                json=flip_request.model_dump()
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
async def get_game_status(request: Request, game_id: int):
    """
    Forwards game_status request to memory_logic service
    """
    verify_jwt_token(request)
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

@app.get("/user_games/{user_id}")
async def get_user_games(request: Request, user_id: str):  # Changed to UUID string
    """
    Forwards user_games request to memory_logic service
    """
    verify_jwt_token(request)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MEMORY_LOGIC_URL}/user_games/{user_id}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get user games: {response.text}"
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

@app.delete("/delete_game/{game_id}")
async def delete_game(request: Request, game_id: int):
    """
    Forwards delete_game request to memory_logic service
    """
    verify_jwt_token(request)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{MEMORY_LOGIC_URL}/delete_game/{game_id}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete game: {response.text}"
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