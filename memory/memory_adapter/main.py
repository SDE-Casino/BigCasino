from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum
import uuid

# Winner enum
class Winner(str, Enum):
    NONE = "none"  # Game still in progress
    DRAW = "draw"  # Game ended in a tie
    PLAYER1 = "player1"  # Player 1 wins
    PLAYER2 = "player2"  # Player 2 wins

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/memory_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Game model
class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(UUID(as_uuid=False), nullable=False)  # Changed to UUID
    size = Column(Integer, nullable=False)  # Size of game (number of pairs)
    winner = Column(String, nullable=True)  # Stores enum string values: "none", "draw", "player1", "player2"
    currentTurn = Column(Boolean, nullable=False)
    
    # Relationship to cards with cascade delete
    cards = relationship("Card", back_populates="game", cascade="all, delete-orphan")

# Card model
class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    localId = Column(Integer, nullable=False)
    gameId = Column(Integer, ForeignKey("games.id"), nullable=False)
    flipped = Column(Boolean, nullable=False)
    ownedBy = Column(Boolean, nullable=True)
    image = Column(Text, nullable=False)
    kindId = Column(Integer, nullable=False)
    
    # Relationship to game
    game = relationship("Game", back_populates="cards")

app = FastAPI(title="Memory Game Adapter API", version="1.0.0", description="API for managing memory games and cards")

@app.on_event("startup")
async def startup_event():
    # Create tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")

class GameCreate(BaseModel):
    userId: str
    size: int
    winner: Optional[str] = None  # Can be "none", "draw", "player1", "player2", or None
    currentTurn: bool = True

class CardCreate(BaseModel):
    localId: int
    gameId: int
    flipped: bool
    ownedBy: Optional[bool] = None  # None=table, False=player1, True=player2
    image: str
    kindId: int

class MoveCardsRequest(BaseModel):
    kindId: int
    player: bool
    gameId: int

class GameUpdate(BaseModel):
    userId: Optional[str] = None
    size: Optional[int] = None
    winner: Optional[str] = None  # Can be "none", "draw", "player1", "player2", or None
    currentTurn: Optional[bool] = None

class CardUpdate(BaseModel):
    localId: Optional[int] = None
    gameId: Optional[int] = None
    flipped: Optional[bool] = None
    ownedBy: Optional[bool] = None
    image: Optional[str] = None
    kindId: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Memory Game Adapter API is running"}

@app.get("/health")
def health_check():
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/games")
def get_games():
    db = SessionLocal()
    try:
        games = db.query(Game).all()
        return {"games": games}
    finally:
        db.close()

@app.get("/games/{game_id}")
def get_game(game_id: int):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        return {"game": game}
    finally:
        db.close()

@app.post("/games")
def create_game(game: GameCreate):
    db = SessionLocal()
    try:
        new_game = Game(
            userId=game.userId,
            size=game.size,
            winner=game.winner,
            currentTurn=game.currentTurn
        )
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return {"game": new_game}
    finally:
        db.close()

@app.put("/games/{game_id}")
def update_game(game_id: int, game_update: GameUpdate):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404

        if game_update.userId is not None:
            game.userId = game_update.userId
        if game_update.size is not None:
            game.size = game_update.size
        if game_update.winner is not None:
            game.winner = game_update.winner
        if game_update.currentTurn is not None:
            game.currentTurn = game_update.currentTurn
            
        db.commit()
        db.refresh(game)
        return {"game": game}
    finally:
        db.close()

@app.delete("/games/{game_id}")
def delete_game(game_id: int):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        
        db.delete(game)
        db.commit()
        return {"message": "Game deleted successfully"}
    finally:
        db.close()


@app.get("/cards")
def get_cards():
    db = SessionLocal()
    try:
        cards = db.query(Card).all()
        return {"cards": cards}
    finally:
        db.close()

@app.get("/cards/{card_id}")
def get_card(card_id: int):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404
        return {"card": card}
    finally:
        db.close()

@app.post("/cards")
def create_card(card: CardCreate):
    db = SessionLocal()
    try:
        new_card = Card(
            localId=card.localId,
            gameId=card.gameId,
            flipped=card.flipped,
            ownedBy=card.ownedBy,
            image=card.image,
            kindId=card.kindId
        )
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return {"card": new_card}
    finally:
        db.close()

@app.put("/cards/{card_id}")
def update_card(card_id: int, card_update: CardUpdate):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404

        if card_update.localId is not None:
            card.localId = card_update.localId
        if card_update.gameId is not None:
            card.gameId = card_update.gameId
        if card_update.flipped is not None:
            card.flipped = card_update.flipped
        if card_update.ownedBy is not None:
            card.ownedBy = card_update.ownedBy
        if card_update.image is not None:
            card.image = card_update.image
        if card_update.kindId is not None:
            card.kindId = card_update.kindId
            
        db.commit()
        db.refresh(card)
        return {"card": card}
    finally:
        db.close()

@app.delete("/cards/{card_id}")
def delete_card(card_id: int):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404
        
        db.delete(card)
        db.commit()
        return {"message": "Card deleted successfully"}
    finally:
        db.close()


@app.get("/games/{game_id}/cards")
def get_cards_for_game(game_id: int):
    db = SessionLocal()
    try:
        cards = db.query(Card).filter(Card.gameId == game_id).all()
        return {"cards": cards}
    finally:
        db.close()


@app.get("/game_state/{game_id}")
def get_game_state(game_id: int):
    db = SessionLocal()
    try:
        # Get game
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        

        

        cards = db.query(Card).filter(Card.gameId == game_id).order_by(Card.localId).all()
        

        table_cards = []
        player1_cards = []
        player2_cards = []
        

        for card in cards:
            card_data = {
                "id": card.id,
                "localId": card.localId,
                "flipped": card.flipped,
                "image": card.image,
                "kindId": card.kindId,
                "ownedBy": card.ownedBy
            }
            

            
            if card.ownedBy is None:
                table_cards.append(card_data)
            elif card.ownedBy is False:
                player1_cards.append(card_data)
            else:  # card.ownedBy is True
                player2_cards.append(card_data)

        game_state = {
            "game": {
                "id": game.id,
                "userId": game.userId,
                "size": game.size,
                "winner": game.winner,
                "currentTurn": game.currentTurn
            },
            "tableCards": table_cards,
            "player1Cards": player1_cards,
            "player2Cards": player2_cards
        }
        
        return game_state
    finally:
        db.close()


@app.put("/flip_card/{card_id}")
def flip_card(card_id: int):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404
        

        card.flipped = not card.flipped

            
        db.commit()
        db.refresh(card)
        return {"card": card}
    finally:
        db.close()


@app.post("/change_turn/{game_id}")
def change_turn(game_id: int):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        

        game.currentTurn = not game.currentTurn

        
        db.commit()
        db.refresh(game)
        return {"game": game}
    finally:
        db.close()


@app.post("/move_cards_to_player")
def move_cards_to_player(request: MoveCardsRequest):
    db = SessionLocal()
    try:

        cards = db.query(Card).filter(
            Card.kindId == request.kindId,
            Card.gameId == request.gameId,
            Card.ownedBy == None
        ).all()

        
        if not cards:
            return {"message": "No cards found with specified kindId on the table", "cards": []}
        
        for card in cards:
            card.ownedBy = request.player
        
        db.commit()

        for card in cards:
            db.refresh(card)

        
        return {"message": f"Moved {len(cards)} card(s) to player", "cards": cards}
    finally:
        db.close()

@app.get("/users/{user_id}/games")
def get_user_games(user_id: str):
    db = SessionLocal()
    try:

        games = db.query(Game).filter(Game.userId == user_id).all()

        
        result = {
            "games": []
        }
        
        for game in games:

            cards = db.query(Card).filter(Card.gameId == game.id).all()
            

            player1_cards = []
            player2_cards = []
            
            for card in cards:
                card_data = {
                    "id": card.id,
                    "localId": card.localId,
                    "flipped": card.flipped,
                    "image": card.image,
                    "kindId": card.kindId,
                    "ownedBy": card.ownedBy
                }
                
                if card.ownedBy is False:
                    player1_cards.append(card_data)
                elif card.ownedBy is True:
                    player2_cards.append(card_data)
            
            game_data = {
                "gameId": game.id,
                "size": game.size,
                "winner": game.winner,
                "player1Cards": player1_cards,
                "player2Cards": player2_cards
            }
            
            result["games"].append(game_data)
        
        return result
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
