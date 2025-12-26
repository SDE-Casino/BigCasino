from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(unique = True, nullable = False)
    password: Mapped[bytes] = mapped_column(nullable = False)

    def __init__(self, username: str, password: bytes):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password