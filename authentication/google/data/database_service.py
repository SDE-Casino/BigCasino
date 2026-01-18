from data.models.users import User, Base
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from datetime import datetime
import os

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(os.getenv('DATABASE_URL'))
        Base.metadata.create_all(self.engine)

    def find_user_by_google_id(self, google_id: str):
        """
        Find a user based on its Google ID
        """
        with Session(self.engine) as session:
            user = session.execute(select(User).filter(User.google_id == google_id)).scalar_one_or_none()
            if not user:
                return None

            return user

    def find_user_by_email(self, email: str):
        """
        Find a user based on its email
        """
        with Session(self.engine) as session:
            user = session.execute(select(User).filter(User.google_email == email)).scalar_one_or_none()
            if not user:
                return None

            return user

    def create_user(self, user_data: dict):
        """
        Create a new google user
        """
        with Session(self.engine) as session:
            new_user = User(
                username=user_data.get('name'),
                google_id=user_data.get('google_id'),
                google_email=user_data.get('email')
            )
            session.add(new_user)
            session.commit()
            user_data['created_at'] = datetime.now()
            user_data['_id'] = new_user.id
            return user_data

database_service = DatabaseService()