from data.database_service import database_service
from data.models.users import User
from typing import Optional

class DatabaseInterface:
    def __init__(self):
        self.db_service = database_service

    def _user_to_dict(self, user: User) -> dict:
        """
        Convert a SQLAlchemy User object to a dictionary
        """
        return {
            '_id': user.id,
            'email': user.google_email,
            'name': user.username,
            'google_id': user.google_id,
        }

    def find_or_create_user_from_google(self, google_profile: dict) -> dict:
        """
        Find or create a user based on Google profile
        """
        google_id = google_profile.get('sub')
        email = google_profile.get('email')

        user = self.db_service.find_user_by_google_id(google_id)

        if not user:
            user = self.db_service.find_user_by_email(email)

            if not user:
                user = self.db_service.create_user({
                    'google_id': google_id,
                    'email': email,
                    'name': google_profile.get('name'),
                })
                return user  # create_user already returns a dict

        # Convert SQLAlchemy User object to dict
        return self._user_to_dict(user)

database_interface = DatabaseInterface()