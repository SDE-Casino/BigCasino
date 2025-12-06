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
    kindId: int

class GameResponse(BaseModel):
    id: int
    userId: int
    winner: Optional[str]  # Can be "none", "draw", "player1", "player2", or None
    currentTurn: bool

class CreateGameResponse(BaseModel):
    game: GameResponse
    cards: List[CardResponse]

class FlipCardRequest(BaseModel):
    game_id: int
    card_id: int

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
                    
                    print(f"Creating card with localId={local_id}, gameId={game_id}, kindId={pair_id}, image={image_data[:50]}...")
                    card_response = await client.post(
                        f"{MEMORY_ADAPTER_URL}/cards",
                        json={
                            "localId": local_id,
                            "gameId": game_id,
                            "flipped": False,
                            "ownedBy": False,  # False means not owned by any player yet
                            "image": image_data,
                            "kindId": pair_id
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

@app.post("/flip_card")
async def flip_card(request: FlipCardRequest):
    """
    Flips a card and handles game logic for matching cards, turn changes, and winner determination.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Call memory_adapter's flip_card endpoint
            flip_response = await client.put(
                f"{MEMORY_ADAPTER_URL}/flip_card/{request.card_id}"
            )
            
            if flip_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to flip card: {flip_response.text}"
                )
            
            # Step 2: Get current game state
            game_state_response = await client.get(
                f"{MEMORY_ADAPTER_URL}/game_state/{request.game_id}"
            )
            
            if game_state_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get game state: {game_state_response.text}"
                )
            
            # Step 3: Store this game state (will be returned at the end)
            stored_game_state = game_state_response.json()
            
            # Step 4: Check if there are exactly 2 flipped cards in tableCards
            table_cards = stored_game_state.get("tableCards", [])
            flipped_cards = [card for card in table_cards if card.get("flipped", False)]
            
            # Step 5: If two flipped cards exist, handle matching logic
            if len(flipped_cards) == 2:
                card1 = flipped_cards[0]
                card2 = flipped_cards[1]
                
                if card1["kindId"] != card2["kindId"]:
                    # Different kindId: flip both cards back and change turn
                    await client.put(f"{MEMORY_ADAPTER_URL}/flip_card/{card1['id']}")
                    await client.put(f"{MEMORY_ADAPTER_URL}/flip_card/{card2['id']}")
                    await client.post(f"{MEMORY_ADAPTER_URL}/change_turn/{request.game_id}")
                else:
                    # Same kindId: move cards to player
                    current_turn = stored_game_state.get("currentTurn", False)
                    await client.post(
                        f"{MEMORY_ADAPTER_URL}/move_cards_to_player",
                        json={
                            "kindId": card1["kindId"],
                            "player": current_turn
                        }
                    )
                    
                    # Get new temporary game state to check if tableCards is empty
                    new_game_state_response = await client.get(
                        f"{MEMORY_ADAPTER_URL}/game_state/{request.game_id}"
                    )
                    
                    if new_game_state_response.status_code == 200:
                        new_game_state = new_game_state_response.json()
                        new_table_cards = new_game_state.get("tableCards", [])
                        
                        # If tableCards is empty, update the winner
                        if len(new_table_cards) == 0:
                            player1_count = len(new_game_state.get("player1Cards", []))
                            player2_count = len(new_game_state.get("player2Cards", []))
                            
                            if player1_count > player2_count:
                                winner = "player1"  # Player 1 wins
                            elif player2_count > player1_count:
                                winner = "player2"  # Player 2 wins
                            else:
                                winner = "draw"  # Tie
                            
                            # Update the game with the winner
                            await client.put(
                                f"{MEMORY_ADAPTER_URL}/games/{request.game_id}",
                                json={"winner": winner}
                            )
            
            # Step 6: Return the stored game state from step 2
            return stored_game_state
                
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