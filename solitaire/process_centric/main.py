from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from solitaire import SolitaireGame
import uuid
import requests
import jwt
import os

load_dotenv()

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

app = FastAPI(title="Solitaire Process-Centric Service", description="Service that exposes the solitaire game functionalities and provide the leaderboard to the UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}

@app.post("/create_game")
def create_game(request: Request):
    """
    Create a new instance for a solitaire game
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    user_id = None
    try:
        decoded = jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        user_id = decoded['sub']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/create_game"
    response = requests.post(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    if user_id:
        leaderboard_url = os.getenv("LEADERBOARD_URL") + "/new_game/" + user_id
        leaderboard_response = requests.post(leaderboard_url)

        if leaderboard_response.status_code != 200:
            raise HTTPException(status_code=leaderboard_response.status_code, detail=leaderboard_response.json()['detail'])

    data = response.json()

    game_id = str(uuid.uuid4())
    games[game_id] = SolitaireGame.from_dict(data['game'])
    return {
        "game_id": game_id,
        "game_state": games[game_id].get_game_state(),
        "game_status": "playing"
    }

@app.post("/draw_cards/{game_id}")
def draw_cards(request: Request, game_id: str):
    """
    Draw cards from the stock pile to talon
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    try:
        jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
def reset_stock(request: Request, game_id: str):
    """
    Reset the stock pile from the talon
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    try:
        jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
def move_card(request: Request, game_id: str, body: MoveCardRequest):
    """
    Move a card from one pile to another

    For parameters:

    Move inside tableau: {column_from: int, column_to: int, number_of_cards: int}

    Move to foundation from tableau: {column_from: int, suit: str}

    Move to tableau from talon: {column_to: int}

    Move to foundation from talon: {suit: str}
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    user_id = None
    try:
        decoded = jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        user_id = decoded['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code = 404, detail="Game not found")

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/move_card"
    json = {
        "game": game.to_dict(),
        **body.dict()
    }
    response = requests.post(url, json=json)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    if response.json().get("game_status") == "won" and user_id:
        leaderboard_url = os.getenv("LEADERBOARD_URL") + "/won_game/" + user_id
        leaderboard_response = requests.post(leaderboard_url)

        if leaderboard_response.status_code != 200:
            raise HTTPException(status_code=leaderboard_response.status_code, detail=leaderboard_response.json()['detail'])

    data = response.json()
    games[game_id] = SolitaireGame.from_dict(data['game'])
    return {
        "game_state": games[game_id].get_game_state(),
        "game_status": data['game_status']
    }

@app.get("/leaderboard")
def get_leaderboard(request: Request):
    """
    Return the leaderboard with stats for all the users
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    try:
        jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    url = os.getenv("LEADERBOARD_URL") + "/leaderboard"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()