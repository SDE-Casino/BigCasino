from data.database_service import database_service
from typing import Optional

class DatabaseInterface:
    def __init__(self):
        self.db_service = database_service

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

        return user

database_interface = DatabaseInterface()