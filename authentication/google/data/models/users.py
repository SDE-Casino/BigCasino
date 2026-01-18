from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "google_users"

    id: Mapped[str] = mapped_column(
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(unique = True, nullable = False)
    google_id: Mapped[str] = mapped_column(unique = True, nullable = True)
    google_email: Mapped[str] = mapped_column(unique = True, nullable = True)

    def __init__(self, username: str, google_id: str = None, google_email: str = None):
        self.id = str(uuid.uuid4())
        self.username = username
        self.google_id = google_id
        self.google_email = google_email