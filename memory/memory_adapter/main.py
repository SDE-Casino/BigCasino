from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from pydantic import BaseModel

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/memory_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Game model
class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, nullable=False)
    winner = Column(Boolean, nullable=True)
    currentTurn = Column(Boolean, nullable=False)
    
    # Relationship to cards
    cards = relationship("Card", back_populates="game")

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

# Pydantic models for requests
class GameCreate(BaseModel):
    userId: int
    winner: bool = None
    currentTurn: bool = True

class CardCreate(BaseModel):
    localId: int
    gameId: int
    flipped: bool
    ownedBy: bool = None
    image: str
    kindId: int

# Dependency to get DB session
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

# Game CRUD operations
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
def update_game(game_id: int, userId: int = None, winner: bool = None, currentTurn: bool = None):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        
        if userId is not None:
            game.userId = userId
        if winner is not None:
            game.winner = winner
        if currentTurn is not None:
            game.currentTurn = currentTurn
            
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

# Card CRUD operations
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
def update_card(card_id: int, localId: int = None, gameId: int = None, flipped: bool = None, ownedBy: bool = None, image: str = None, kindId: int = None):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404
        
        if localId is not None:
            card.localId = localId
        if gameId is not None:
            card.gameId = gameId
        if flipped is not None:
            card.flipped = flipped
        if ownedBy is not None:
            card.ownedBy = ownedBy
        if image is not None:
            card.image = image
        if kindId is not None:
            card.kindId = kindId
            
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

# Additional endpoint to get cards for a specific game
@app.get("/games/{game_id}/cards")
def get_cards_for_game(game_id: int):
    db = SessionLocal()
    try:
        cards = db.query(Card).filter(Card.gameId == game_id).all()
        return {"cards": cards}
    finally:
        db.close()

# Game state endpoint
@app.get("/game_state/{game_id}")
def get_game_state(game_id: int):
    db = SessionLocal()
    try:
        # Get the game
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return {"error": "Game not found"}, 404
        
        # Get all cards for this game
        cards = db.query(Card).filter(Card.gameId == game_id).all()
        
        # Initialize card lists
        table_cards = []
        player1_cards = []
        player2_cards = []
        
        # Read the cover image from cover_image.txt
        try:
            with open('cover_image.txt', 'r') as f:
                cover_image = f.read().strip()
        except Exception as e:
            print(f"Error reading cover_image.txt: {e}")
            exit(1)
        
        # Categorize cards based on ownedBy field
        for card in cards:
            card_data = {
                "id": card.id,
                "localId": card.localId,
                "flipped": card.flipped,
                "image": card.image,
                "kindId": card.kindId
            }
            
            if card.ownedBy is None:
                table_cards.append(card_data)
            elif card.ownedBy is False:
                player1_cards.append(card_data)
            else:  # card.ownedBy is True
                player2_cards.append(card_data)
        
        # Construct the response
        game_state = {
            "coverImage": cover_image,
            "currentTurn": game.currentTurn,
            "tableCards": table_cards,
            "player1Cards": player1_cards,
            "player2Cards": player2_cards
        }
        
        return game_state
    finally:
        db.close()

# Endpoint to flip a card
@app.put("/flp_card/{card_id}")
def flip_card(card_id: int):
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is None:
            return {"error": "Card not found"}, 404
        
        # Flip the card's flipped status
        card.flipped = not card.flipped
            
        db.commit()
        db.refresh(card)
        return {"card": card}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)