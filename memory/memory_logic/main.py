from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import random
import copy
from typing import List, Optional

app = FastAPI(title="Memory Logic Service", description="A simple FastAPI service for memory logic operations")

# Pydantic models for request/response
class CreateGameRequest(BaseModel):
    userId: str  # Changed to UUID string
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
    local_id: int

# Service URLs
MEMORY_ADAPTER_URL = "http://memory_adapter:8000"
IMAGE_ADAPTER_URL = "http://image_adapter:8000"

def strip_private_info(game_state: dict) -> dict:
    """
    Creates a new dictionary where image and kindId are included only if flipped is true.
    Only processes cards in tableCards, leaving player1Cards and player2Cards unchanged.
    """
    # Create a deep copy of the game state to avoid modifying the original
    stripped_state = copy.deepcopy(game_state)
    
    # Process tableCards to remove private info from unflipped cards
    table_cards = stripped_state.get("tableCards", [])
    for card in table_cards:
        if not card.get("flipped", False):
            # Remove private info for unflipped cards
            card.pop("image", None)
            card.pop("kindId", None)
    
    print(f"DEBUG strip_private_info: player1Cards count={len(stripped_state.get('player1Cards', []))}, player2Cards count={len(stripped_state.get('player2Cards', []))}")
    
    return stripped_state

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
                    "size": request.size,
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
                    # Build card data with explicit None for ownedBy
                    card_data = {
                        "localId": local_id,
                        "gameId": game_id,
                        "flipped": False,
                        "image": image_data,
                        "kindId": pair_id
                    }
                    # Explicitly set ownedBy to None (null in JSON)
                    card_data["ownedBy"] = None
                    card_response = await client.post(
                        f"{MEMORY_ADAPTER_URL}/cards",
                        json=card_data
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
                    json={"localId": index}
                )
            
            # Get the game state from memory_adapter
            game_state_response = await client.get(f"{MEMORY_ADAPTER_URL}/game_state/{game_id}")
            
            if game_state_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get game state: {game_state_response.text}"
                )
            
            game_state = game_state_response.json()
            return strip_private_info(game_state)
                
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
            # Step 1: Find the card by localId and gameId
            cards_response = await client.get(
                f"{MEMORY_ADAPTER_URL}/games/{request.game_id}/cards"
            )
            
            if cards_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get cards: {cards_response.text}"
                )
            
            cards = cards_response.json()["cards"]
            # Find the card with matching localId
            card_to_flip = None
            for card in cards:
                if card["localId"] == request.local_id:
                    card_to_flip = card
                    break
            
            if card_to_flip is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Card with localId {request.local_id} not found"
                )
            
            # Step 2: Call memory_adapter's flip_card endpoint with the actual card id
            flip_response = await client.put(
                f"{MEMORY_ADAPTER_URL}/flip_card/{card_to_flip['id']}"
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
            print(f"DEBUG flip_card: Got game state, currentTurn={stored_game_state.get('game', {}).get('currentTurn')}")
            
            # Step 4: Check if there are exactly 2 flipped cards in tableCards
            table_cards = stored_game_state.get("tableCards", [])
            flipped_cards = [card for card in table_cards if card.get("flipped", False)]
            
            # Step 5: If two flipped cards exist, handle matching logic
            if len(flipped_cards) == 2:
                # Sort flipped cards by localId to ensure consistent ordering
                flipped_cards.sort(key=lambda card: card.get("localId", 0))
                card1 = flipped_cards[0]
                card2 = flipped_cards[1]
                
                if card1["kindId"] != card2["kindId"]:
                    # Different kindId: flip both cards back and change turn
                    await client.put(f"{MEMORY_ADAPTER_URL}/flip_card/{card1['id']}")
                    await client.put(f"{MEMORY_ADAPTER_URL}/flip_card/{card2['id']}")
                    await client.post(f"{MEMORY_ADAPTER_URL}/change_turn/{request.game_id}")
                else:
                    # Same kindId: move cards to player
                    # Get fresh game state to get the current turn
                    fresh_game_state_response = await client.get(
                        f"{MEMORY_ADAPTER_URL}/game_state/{request.game_id}"
                    )
                    
                    if fresh_game_state_response.status_code == 200:
                        fresh_game_state = fresh_game_state_response.json()
                        current_turn = fresh_game_state.get("game", {}).get("currentTurn", False)
                    else:
                        # Fallback to stored state if fresh fetch fails
                        current_turn = stored_game_state.get("game", {}).get("currentTurn", False)
                    
                    print(f"DEBUG: Moving cards to player. currentTurn={current_turn}, kindId={card1['kindId']}, gameId={request.game_id}")
                    await client.post(
                        f"{MEMORY_ADAPTER_URL}/move_cards_to_player",
                        json={
                            "kindId": card1["kindId"],
                            "player": current_turn,
                            "gameId": request.game_id
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
            
            # Step 6: Return the stored game state from step 2 with private info stripped
            return strip_private_info(stored_game_state)
                
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

@app.get("/game_status/{game_id}")
async def get_game_status(game_id: int):
    """
    Returns the game state with private information stripped.
    Image and kindId are only included for flipped cards in tableCards.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get the game state from memory_adapter
            game_state_response = await client.get(f"{MEMORY_ADAPTER_URL}/game_state/{game_id}")
            
            if game_state_response.status_code != 200:
                raise HTTPException(
                    status_code=404,
                    detail=f"Game not found: {game_state_response.text}"
                )
            
            game_state = game_state_response.json()
            return strip_private_info(game_state)
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory adapter: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_detail = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

@app.get("/user_games/{user_id}")
async def get_user_games(user_id: str):  # Changed to UUID string
    """
    Returns all games for a specific user with their cards categorized by player.
    Calls memory_adapter's /users/{user_id}/games endpoint.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get user games from memory_adapter
            response = await client.get(f"{MEMORY_ADAPTER_URL}/users/{user_id}/games")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get user games: {response.text}"
                )
            
            return response.json()
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory adapter: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_detail = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

@app.delete("/delete_game/{game_id}")
async def delete_game(game_id: int):
    """
    Deletes a game by forwarding the request to memory_adapter.
    This will cascade delete all associated cards.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Forward delete request to memory_adapter
            response = await client.delete(f"{MEMORY_ADAPTER_URL}/games/{game_id}")
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Game not found: {game_id}"
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete game: {response.text}"
                )
            
            return response.json()
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with memory adapter: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_detail = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )