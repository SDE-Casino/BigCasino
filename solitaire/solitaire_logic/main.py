from solitaire import SolitaireGame
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import Union
import uuid
from fastapi.middleware.cors import CORSMiddleware


class MoveCardInsideTableauRequest(BaseModel):
    game: dict
    column_from: int
    column_to: int
    number_of_cards: int = 1

class MoveCardToFoundationRequest(BaseModel):
    game: dict
    column_from: int
    suit: str

class MoveCardToTableauRequest(BaseModel):
    game: dict
    column_to: int

class MoveCardToFoundationFromTalon(BaseModel):
    game: dict
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

@app.post("/create_game")
def create_game():
    """
    Create a new instance for a solitaire game
    """
    game = SolitaireGame()
    return {
        "game": game.to_dict(),
        "game_status": "playing"
    }


@app.post("/move_card")
def move_card(move_request: MoveCardRequest):
    """
    Move a card from one pile to another

    For parameters:

    Move inside tableau: {column_from: int, column_to: int, number_of_cards: int}

    Move to foundation from tableau: {column_from: int, suit: str}

    Move to tableau from talon: {column_to: int}

    Move to foundation from talon: {suit: str}
    """
    game = SolitaireGame.from_dict(move_request.game)
    print(game)
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
                    "game": game.to_dict(),
                    "game_status": "won"
                }
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))
    elif isinstance(move_request, MoveCardToFoundationFromTalon):
        try:
            game.move_card_to_foundation_from_talon(move_request.suit)

            if game.check_win():
                return {
                    "game": game.to_dict(),
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
        "game": game.to_dict(),
        "game_status": "playing"
    }
