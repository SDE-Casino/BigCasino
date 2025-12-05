from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import random
from typing import List, Optional

app = FastAPI(title="Memory Logic Service", description="A simple FastAPI service for memory logic operations")

# Pydantic models for request/response
class CreateGameRequest(BaseModel):
    userId: int
    size: int

class CardResponse(BaseModel):
    id: int
    localId: int
    gameId: int
    flipped: bool
    ownedBy: Optional[bool]
    image: str

class GameResponse(BaseModel):
    id: int
    userId: int
    winner: Optional[bool]
    currentTurn: bool

class CreateGameResponse(BaseModel):
    game: GameResponse
    cards: List[CardResponse]

# Service URLs
MEMORY_ADAPTER_URL = "http://memory_adapter:8000"
IMAGE_ADAPTER_URL = "http://image_adapter:8000"

@app.get("/")
async def root():
    return {"message": "Memory Logic Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/create_game")
async def create_game(request: CreateGameRequest):
    """
    Creates a new memory game with the specified userId and size.
    Creates 2*size cards in pairs, with each pair having its own localId and image.
    """
    try:
        print(f"Creating game with userId={request.userId}, size={request.size}")
        # Create the game first
        async with httpx.AsyncClient() as client:
            # Create a new game with winner=None and currentTurn=False
            game_response = await client.post(
                f"{MEMORY_ADAPTER_URL}/games",
                json={
                    "userId": request.userId,
                    "currentTurn": False
                }
            )
            
            print(f"Game response status: {game_response.status_code}")
            print(f"Game response text: {game_response.text}")
            
            if game_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create game: {game_response.text}"
                )
            
            game_data = game_response.json()["game"]
            game_id = game_data["id"]
            print(f"Created game with ID: {game_id}")
            
            # Create cards for the game
            cards = []
            # We need to create size pairs of cards (2*size cards total)
            for pair_id in range(request.size):
                # Get an image for this pair
                image_response = await client.get(f"{IMAGE_ADAPTER_URL}/image/base64")
                
                if image_response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to get image: {image_response.text}"
                    )
                
                image_data = image_response.json()["image"]
                
                # Create two cards with the same image (a pair)
                for card_in_pair in range(2):
                    # Calculate localId: sequential from 0 to 2*size-1
                    local_id = pair_id * 2 + card_in_pair
                    
                    print(f"Creating card with localId={local_id}, gameId={game_id}, image={image_data[:50]}...")
                    card_response = await client.post(
                        f"{MEMORY_ADAPTER_URL}/cards",
                        json={
                            "localId": local_id,
                            "gameId": game_id,
                            "flipped": False,
                            "ownedBy": False,  # False means not owned by any player yet
                            "image": image_data
                        }
                    )
                    
                    print(f"Card response status: {card_response.status_code}")
                    print(f"Card response text: {card_response.text}")
                    
                    if card_response.status_code != 200:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to create card: {card_response.text}"
                        )
                    
                    card_data = card_response.json()["card"]
                    cards.append(card_data)
            
            # Shuffle the cards to randomize their positions
            random.shuffle(cards)
            
            # Update all cards with their new localId positions after shuffling
            for index, card in enumerate(cards):
                await client.put(
                    f"{MEMORY_ADAPTER_URL}/cards/{card['id']}",
                    params={"localId": index}
                )
            
            # Get the game state from memory_adapter
            game_state_response = await client.get(f"{MEMORY_ADAPTER_URL}/game_state/{game_id}")
            
            if game_state_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get game state: {game_state_response.text}"
                )
            
            game_state = game_state_response.json()
            return game_state
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with other services: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_detail = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )