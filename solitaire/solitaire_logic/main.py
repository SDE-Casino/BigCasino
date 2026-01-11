from solitaire import SolitaireGame
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import Union
import uuid
from fastapi.middleware.cors import CORSMiddleware


class MoveCardInsideTableauRequest(BaseModel):
    column_from: int
    column_to: int
    number_of_cards: int = 1

class MoveCardToFoundationRequest(BaseModel):
    column_from: int
    suit: str

class MoveCardToTableauRequest(BaseModel):
    column_to: int

class MoveCardToFoundationFromTalon(BaseModel):
    suit: str

MoveCardRequest = Union [
    MoveCardInsideTableauRequest,
    MoveCardToFoundationRequest,
    MoveCardToTableauRequest,
    MoveCardToFoundationFromTalon
]

app = FastAPI(title="Solitaire Logic Service", description="Manages all the game logic for Solitaire game")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


games = {}

@app.post("/create_game")
def create_game():
    """
    Create a new instance for a solitaire game
    """
    game_id = str(uuid.uuid4())
    game = SolitaireGame()
    games[game_id] = game
    return {
        "game_id": game_id,
        "game_state": game.get_game_state()
    }

@app.post("/draw_cards/{game_id}")
def draw_cards(game_id: str):
    """
    Draw cards from the stock pile to talon
    """
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        game.draw_from_stock()
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "game_state": game.get_game_state(),
        "game_status": "playing"
    }

@app.post("/reset_stock/{game_id}")
def reset_stock(game_id: str):
    """
    Reset the stock pile from the talon
    """
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        game.reload_stock_from_talon()
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "game_state": game.get_game_state(),
        "game_status": "playing"
    }

@app.post("/move_card/{game_id}")
def move_card(game_id: str, move_request: MoveCardRequest):
    """
    Move a card from one pile to another

    For parameters:

    Move inside tableau: {column_from: int, column_to: int, number_of_cards: int}

    Move to foundation from tableau: {column_from: int, suit: str}

    Move to tableau from talon: {column_to: int}

    Move to foundation from talon: {suit: str}
    """
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code = 404, detail="Game not found")

    if isinstance(move_request, MoveCardInsideTableauRequest):
        try:
            game.move_cards_inside_tableau(
                move_request.column_from,
                move_request.column_to,
                move_request.number_of_cards
            )
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))
    elif isinstance(move_request, MoveCardToFoundationRequest):
        try:
            game.move_card_to_foundation_from_tableau(
                move_request.column_from,
                move_request.suit
            )

            if game.check_win():
                return {
                    "game_state": game.get_game_state(),
                    "game_status": "won"
                }
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))
    elif isinstance(move_request, MoveCardToFoundationFromTalon):
        try:
            game.move_card_to_foundation_from_talon(move_request.suit)

            if game.check_win():
                return {
                    "game_state": game.get_game_state(),
                    "game_status": "won"
                }
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))
    elif isinstance(move_request, MoveCardToTableauRequest):
        try:
            game.move_card_to_tableau_from_talon(
                move_request.column_to
            )
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    return {
        "game_state": game.get_game_state(),
        "game_status": "playing"
    }
