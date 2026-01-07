from fastapi import FastAPI, HTTPException
from models.leaderboard import Base, Leaderboard
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)

app = FastAPI()

@app.get("/leaderboard")
def get_user_name():
    with Session(engine) as session:
        leaderboard = session.execute(select(Leaderboard)).scalars().all()
        if leaderboard is None:
            raise HTTPException(status_code=404, detail="No leaderboard data found")

        return leaderboard


@app.post("/new_game/{user_id}")
def new_game(user_id: str):
    with Session(engine) as session:
        leaderboard_user = session.execute(select(Leaderboard).filter(Leaderboard.user_id == user_id)).scalar_one_or_none()

        if leaderboard_user:
            leaderboard_user.start_new_game()
            session.commit()
            return {
                'user_id': leaderboard_user.user_id,
                'played_games': leaderboard_user.played_games,
                'games_won': leaderboard_user.games_won
            }
        else:
            new_leaderboard_user = Leaderboard(user_id=user_id)
            new_leaderboard_user.start_new_game()
            session.add(new_leaderboard_user)
            session.commit()
            return {
                'user_id': new_leaderboard_user.user_id,
                'played_games': 1,
                'games_won': 0
            }

@app.post("/won_game/{user_id}")
def won_name(user_id: str):
    with Session(engine) as session:
        leaderboard_user = session.execute(select(Leaderboard).filter(Leaderboard.user_id == user_id)).scalar_one_or_none()

        if leaderboard_user is None:
            raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")

        leaderboard_user.won_a_game()
        session.commit()
        return {
            'user_id': leaderboard_user.user_id,
            'played_games': leaderboard_user.played_games,
            'games_won': leaderboard_user.games_won
        }