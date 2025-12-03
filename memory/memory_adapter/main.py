from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
import uuid
from datetime import datetime
import os
import sqlite3
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Database setup
import os
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/memory_db")
SQLALCHEMY_DATABASE_URL = DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class CardModel(BaseModel):
    cardId: int
    image: str  # base64 encoded image

class DeckModel(BaseModel):
    gameId: str
    card_amount: int
    cards: List[CardModel]

class PlayerModel(BaseModel):
    userId: str
    cards: List[CardModel]

class GameModel(BaseModel):
    userId: str
    deckId: str
    size: int
    tableState: List[Dict]  # List of cards with flipped state
    player1: PlayerModel
    player2: PlayerModel
    currentTurn: bool  # True for player1, False for player2

class CardCreate(BaseModel):
    cardId: int
    image: str

class DeckCreate(BaseModel):
    gameId: str
    card_amount: int
    cards: List[CardCreate]

class GameCreate(BaseModel):
    userId: str
    size: int
    player1_userId: str
    player2_userId: str
    cards: List[CardCreate]  # Cards to create for this game's deck

# Response Models
class CardResponse(BaseModel):
    id: str
    cardId: int
    image: str
    deckId: str

    class Config:
        from_attributes = True

class DeckResponse(BaseModel):
    id: str
    gameId: str
    card_amount: int
    cards: List[CardResponse]

    class Config:
        from_attributes = True

class GameResponse(BaseModel):
    id: str
    userId: str
    deckId: str
    size: int
    tableState: str  # JSON string
    player1: str  # JSON string
    player2: str  # JSON string
    currentTurn: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# SQLAlchemy Database Models
class Card(Base):
    __tablename__ = "cards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cardId = Column(Integer, nullable=False)
    image = Column(Text, nullable=False)  # base64 encoded image
    deckId = Column(String, ForeignKey("decks.id"), nullable=False)
    
    # Relationship
    deck = relationship("Deck", back_populates="cards")

class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    gameId = Column(String, nullable=False)
    card_amount = Column(Integer, nullable=False)
    
    # Relationships
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="deck")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String, nullable=False)
    deckId = Column(String, ForeignKey("decks.id"), nullable=False)
    size = Column(Integer, nullable=False)
    tableState = Column(Text, nullable=False)  # JSON string
    player1 = Column(Text, nullable=False)  # JSON string
    player2 = Column(Text, nullable=False)  # JSON string
    currentTurn = Column(Boolean, nullable=False, default=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deck = relationship("Deck", back_populates="games")

# FastAPI App
app = FastAPI(title="Memory Adapter API", description="API for Memory Game")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables
@app.on_event("startup")
def startup_event():
    # Retry database connection a few times to handle startup race conditions
    import time
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to connect to database after {max_retries} attempts: {e}")
                raise
            print(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Memory Adapter API is running"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Deck endpoints (read-only, as decks are managed through games)
@app.get("/decks/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: str, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

# Game endpoints
@app.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    # Create a new deck for this game
    db_deck = Deck(
        gameId="",  # Will be set after game is created
        card_amount=len(game.cards)
    )
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    
    # Create cards for the deck
    for card_data in game.cards:
        db_card = Card(
            cardId=card_data.cardId,
            image=card_data.image,
            deckId=db_deck.id
        )
        db.add(db_card)
    
    # Initialize table state with cards from deck (all flipped down)
    table_cards = []
    for card_data in game.cards:
        table_cards.append({
            "cardId": card_data.cardId,
            "image": card_data.image,
            "isFlipped": False
        })
    
    # Initialize players with empty cards
    import json
    player1_data = json.dumps({"userId": game.player1_userId, "cards": []})
    player2_data = json.dumps({"userId": game.player2_userId, "cards": []})
    
    # Create the game
    db_game = Game(
        userId=game.userId,
        deckId=db_deck.id,
        size=game.size,
        tableState=json.dumps(table_cards),
        player1=player1_data,
        player2=player2_data,
        currentTurn=True
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    # Update the deck with the game ID
    db_deck.gameId = db_game.id
    db.commit()
    
    return db_game

@app.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.get("/games", response_model=List[GameResponse])
def get_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = db.query(Game).offset(skip).limit(limit).all()
    return games

@app.put("/games/{game_id}/flip", response_model=GameResponse)
def flip_card(game_id: str, card_index: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    import json
    table_state = json.loads(game.tableState)
    
    if card_index < 0 or card_index >= len(table_state):
        raise HTTPException(status_code=400, detail="Invalid card index")
    
    # Flip the card
    table_state[card_index]["isFlipped"] = not table_state[card_index]["isFlipped"]
    game.tableState = json.dumps(table_state)
    game.updatedAt = datetime.utcnow()
    
    db.commit()
    db.refresh(game)
    return game

@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get the deck associated with this game
    deck = db.query(Deck).filter(Deck.id == game.deckId).first()
    if deck:
        # Delete the deck (this will also delete all cards due to cascade)
        db.delete(deck)
    
    # Delete the game
    db.delete(game)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)