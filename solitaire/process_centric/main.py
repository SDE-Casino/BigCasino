from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/create_game")
def create_game(request: Request):
    """
    Create a new instance for a solitaire game
    """
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    jwt_token = jwt_token.replace("Bearer ", "")

    print(f"[SOLITAIRE SERVICE] Verifying token: {jwt_token[:50]}...")  # DEBUG LOG
    print(f"[SOLITAIRE SERVICE] JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')[:20]}...")  # DEBUG LOG
    print(f"[SOLITAIRE SERVICE] JWT_ALGORITHM: {os.getenv('JWT_ALGORITHM')}")  # DEBUG LOG

    try:
        decoded = jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        print(f"[SOLITAIRE SERVICE] Token decoded successfully: {decoded}")  # DEBUG LOG
    except jwt.ExpiredSignatureError as e:
        print(f"[SOLITAIRE SERVICE] Token expired error: {e}")  # DEBUG LOG
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"[SOLITAIRE SERVICE] Invalid token error: {e}")  # DEBUG LOG
        raise HTTPException(status_code=401, detail="Invalid token")

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/create_game"
    response = requests.post(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()

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

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/draw_cards/" + game_id
    response = requests.post(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()

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

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/reset_stock/" + game_id
    response = requests.post(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()

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

    try:
        jwt.decode(jwt_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    url = os.getenv("LOGIC_LAYER_SERVICE_URL") + "/move_card/" + game_id
    response = requests.post(url, json=body.dict())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()
