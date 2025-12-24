from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default = lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(unique = True, nullable = False)
    password: Mapped[str] = mapped_column(nullable = False)