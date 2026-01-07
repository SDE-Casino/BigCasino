from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
import uuid

class Base(DeclarativeBase):
    pass

class Leaderboard(Base):
    __tablename__ = "leaderboard"

    user_id: Mapped[str] = mapped_column(primary_key = True, nullable = False)
    played_games: Mapped[int] = mapped_column(default = 0, nullable = False)
    games_won: Mapped[int] = mapped_column(default = 0, nullable = False)

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.played_games = 0
        self.games_won = 0

    def start_new_game(self):
        self.played_games += 1

    def won_a_game(self):
        self.games_won += 1