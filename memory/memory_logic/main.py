from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
import uuid
from datetime import datetime
import os
import json
import random
import httpx

# Configuration
MEMORY_ADAPTER_URL = os.environ.get("MEMORY_ADAPTER_URL", "http://memory_adapter:8001")
IMAGE_ADAPTER_URL = os.environ.get("IMAGE_ADAPTER_URL", "http://image_adapter:8000")

# Pydantic Models
class CardModel(BaseModel):
    cardId: int
    image: str  # base64 encoded image
    isFlipped: bool = False
    isCollected: bool = False

class PlayerModel(BaseModel):
    cards: List[Dict]  # Player's collected cards (stored as dicts)

class GameStateModel(BaseModel):
    id: str
    userId: str
    deckId: str
    size: int
    tableState: List[Dict]  # List of cards with flipped state
    player1: PlayerModel
    player2: PlayerModel
    currentTurn: bool  # True for player1, False for player2
    isGameOver: bool = False
    winner: Optional[str] = None  # "player1" or "player2"

class CreateGameRequest(BaseModel):
    userId: str
    size: int  # Number of pairs of cards (total cards will be size * 2)

class FlipCardRequest(BaseModel):
    game_id: str
    card_index: int
    player: str  # "player1" or "player2"

class FlipCardResponse(BaseModel):
    game_state: GameStateModel
    match_found: bool
    cards_collected: List[Dict]  # Cards that were collected if a match was found

# FastAPI App
app = FastAPI(title="Memory Logic API", description="API for Memory Game Logic")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions to communicate with memory_adapter
async def get_game_from_adapter(game_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MEMORY_ADAPTER_URL}/games/{game_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Game not found")
        response.raise_for_status()
        return response.json()

async def get_image_from_image_adapter():
    """Get a base64 encoded image from the image_adapter service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{IMAGE_ADAPTER_URL}/image/base64")
        response.raise_for_status()
        return response.json()["image"]

async def create_game_in_adapter(user_id: str, size: int):
    # Create cards for the game by fetching images from the image_adapter service
    cards = []
    
    # Get unique images for each pair of cards
    for i in range(size):
        image = await get_image_from_image_adapter()
        cards.append({"cardId": i, "image": image})
        cards.append({"cardId": i, "image": image})
    
    # Shuffle the cards
    random.shuffle(cards)
    
    game_data = {
        "userId": user_id,
        "size": size,
        "cards": cards
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MEMORY_ADAPTER_URL}/games", json=game_data)
        response.raise_for_status()
        return response.json()

async def update_card_flip_in_adapter(game_id: str, card_index: int):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{MEMORY_ADAPTER_URL}/games/{game_id}/flip?card_index={card_index}")
        response.raise_for_status()
        return response.json()

async def update_table_state_in_adapter(game_id: str, table_state: List[Dict]):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{MEMORY_ADAPTER_URL}/games/{game_id}/table-state", json=table_state)
        response.raise_for_status()
        return response.json()

async def update_player_data_in_adapter(game_id: str, player_num: int, player_data: Dict):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{MEMORY_ADAPTER_URL}/games/{game_id}/player/{player_num}", json=player_data)
        response.raise_for_status()
        return response.json()

async def update_turn_in_adapter(game_id: str, current_turn: bool):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{MEMORY_ADAPTER_URL}/games/{game_id}/turn?current_turn={current_turn}")
        response.raise_for_status()
        return response.json()

async def delete_game_in_adapter(game_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{MEMORY_ADAPTER_URL}/games/{game_id}")
        response.raise_for_status()
        return response

# Game logic functions
def convert_adapter_game_to_game_state(adapter_game: dict) -> GameStateModel:
    """Convert the adapter game format to our game state model"""
    table_state = json.loads(adapter_game["tableState"])
    player1_data = json.loads(adapter_game["player1"])
    player2_data = json.loads(adapter_game["player2"])
    
    # Convert player data to PlayerModel
    player1 = PlayerModel(cards=player1_data.get("cards", []))
    player2 = PlayerModel(cards=player2_data.get("cards", []))
    
    # Check if game is over
    is_game_over = len(table_state) == 0 or all(card.get("isCollected", False) for card in table_state)
    winner = None
    
    if is_game_over:
        player1_score = len(player1.cards)
        player2_score = len(player2.cards)
        if player1_score > player2_score:
            winner = "player1"
        elif player2_score > player1_score:
            winner = "player2"
        else:
            winner = "tie"  # It's a tie
    
    return GameStateModel(
        id=adapter_game["id"],
        userId=adapter_game["userId"],
        deckId=adapter_game["deckId"],
        size=adapter_game["size"],
        tableState=table_state,
        player1=player1,
        player2=player2,
        currentTurn=adapter_game["currentTurn"],
        isGameOver=is_game_over,
        winner=winner
    )

def check_for_match(table_state: List[Dict], flipped_indices: List[int]) -> bool:
    """Check if the flipped cards form a match"""
    if len(flipped_indices) != 2:
        return False
    
    card1 = table_state[flipped_indices[0]]
    card2 = table_state[flipped_indices[1]]
    
    # Check if the cardIds match (same image)
    return card1["cardId"] == card2["cardId"]

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Memory Logic API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/games", response_model=GameStateModel, status_code=status.HTTP_201_CREATED)
async def create_game(request: CreateGameRequest):
    """Create a new memory game"""
    # Create the game through the adapter
    adapter_game = await create_game_in_adapter(request.userId, request.size)
    
    # Convert to our game state model
    game_state = convert_adapter_game_to_game_state(adapter_game)
    
    return game_state

@app.get("/games/{game_id}", response_model=GameStateModel)
async def get_game(game_id: str):
    """Get a game by ID"""
    adapter_game = await get_game_from_adapter(game_id)
    game_state = convert_adapter_game_to_game_state(adapter_game)
    return game_state

@app.post("/games/{game_id}/flip", response_model=FlipCardResponse)
async def flip_card(game_id: str, card_index: int, player: str):
    """Flip a card and handle game logic"""
    # Validate player
    if player not in ["player1", "player2"]:
        raise HTTPException(status_code=400, detail="Player must be 'player1' or 'player2'")
    
    # Get the current game state
    adapter_game = await get_game_from_adapter(game_id)
    game_state = convert_adapter_game_to_game_state(adapter_game)
    
    # Check if it's the player's turn
    if (player == "player1" and not game_state.currentTurn) or \
       (player == "player2" and game_state.currentTurn):
        raise HTTPException(status_code=400, detail="It's not your turn")
    
    # Check if the game is already over
    if game_state.isGameOver:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    # Validate card index
    if card_index < 0 or card_index >= len(game_state.tableState):
        raise HTTPException(status_code=400, detail="Invalid card index")
    
    # Check if the card is already collected
    if game_state.tableState[card_index].get("isCollected", False):
        raise HTTPException(status_code=400, detail="Card is already collected")
    
    # Check if the card is already flipped
    if game_state.tableState[card_index].get("isFlipped", False):
        raise HTTPException(status_code=400, detail="Card is already flipped")
    
    # Flip the card
    await update_card_flip_in_adapter(game_id, card_index)
    
    # Get the updated game state
    adapter_game = await get_game_from_adapter(game_id)
    game_state = convert_adapter_game_to_game_state(adapter_game)
    
    # Find all currently flipped cards
    flipped_indices = [i for i, card in enumerate(game_state.tableState) 
                      if card.get("isFlipped", False) and not card.get("isCollected", False)]
    
    match_found = False
    cards_collected = []
    
    # If two cards are flipped, check for a match
    if len(flipped_indices) == 2:
        match_found = check_for_match(game_state.tableState, flipped_indices)
        
        if match_found:
            # Mark cards as collected and add to player's collection
            cards_to_collect = []
            for idx in flipped_indices:
                card = game_state.tableState[idx]
                card["isCollected"] = True
                card["isFlipped"] = False
                cards_to_collect.append(card)
            
            # Add cards to the current player's collection
            if player == "player1":
                game_state.player1.cards.extend(cards_to_collect)
                player_num = 1
            else:
                game_state.player2.cards.extend(cards_to_collect)
                player_num = 2
            
            cards_collected = cards_to_collect
            
            # Update the table state in the adapter
            await update_table_state_in_adapter(game_id, game_state.tableState)
            
            # Update player data in the adapter
            if player == "player1":
                player_data = {"cards": game_state.player1.cards}
            else:
                player_data = {"cards": game_state.player2.cards}
            await update_player_data_in_adapter(game_id, player_num, player_data)
        else:
            # No match, flip cards back after a delay
            # For now, we'll just switch turns
            game_state.currentTurn = not game_state.currentTurn
            
            # Update the turn in the adapter
            await update_turn_in_adapter(game_id, game_state.currentTurn)
    
    # Check if the game is over
    all_cards_collected = all(card.get("isCollected", False) for card in game_state.tableState)
    if all_cards_collected:
        game_state.isGameOver = True
        player1_score = len(game_state.player1.cards)
        player2_score = len(game_state.player2.cards)
        
        if player1_score > player2_score:
            game_state.winner = "player1"
        elif player2_score > player1_score:
            game_state.winner = "player2"
        else:
            game_state.winner = "tie"
    
    return FlipCardResponse(
        game_state=game_state,
        match_found=match_found,
        cards_collected=cards_collected
    )

@app.post("/games/{game_id}/end-turn")
async def end_turn(game_id: str, player: str):
    """End the current player's turn"""
    # Validate player
    if player not in ["player1", "player2"]:
        raise HTTPException(status_code=400, detail="Player must be 'player1' or 'player2'")
    
    # Get the current game state
    adapter_game = await get_game_from_adapter(game_id)
    game_state = convert_adapter_game_to_game_state(adapter_game)
    
    # Check if it's the player's turn
    if (player == "player1" and not game_state.currentTurn) or \
       (player == "player2" and game_state.currentTurn):
        raise HTTPException(status_code=400, detail="It's not your turn")
    
    # Switch turns
    game_state.currentTurn = not game_state.currentTurn
    
    # Update the turn in the adapter
    await update_turn_in_adapter(game_id, game_state.currentTurn)
    
    # Get the updated game state
    adapter_game = await get_game_from_adapter(game_id)
    game_state = convert_adapter_game_to_game_state(adapter_game)
    
    return game_state

@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: str):
    """Delete a game"""
    await delete_game_in_adapter(game_id)
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)