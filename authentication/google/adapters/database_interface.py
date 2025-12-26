from data.database_service import database_service
from typing import Optional

class DatabaseInterface:
    def __init__(self):
        self.db_service = database_service

    def find_or_create_user_from_google(self, google_profile: dict) -> dict:
        """Trova o crea utente dal profilo Google"""
        google_id = google_profile.get('sub')
        email = google_profile.get('email')

        # Cerca utente esistente
        user = self.db_service.find_user_by_google_id(google_id)

        if not user:
            # Se non esiste, prova a cercare per email
            user = self.db_service.find_user_by_email(email)

            if user:
                # Aggiorna con Google ID
                user = self.db_service.update_user(user['_id'], {
                    'google_id': google_id,
                    'picture': google_profile.get('picture')
                })
            else:
                # Crea nuovo utente
                user = self.db_service.create_user({
                    'google_id': google_id,
                    'email': email,
                    'name': google_profile.get('name'),
                    'given_name': google_profile.get('given_name'),
                    'family_name': google_profile.get('family_name'),
                    'picture': google_profile.get('picture'),
                    'email_verified': google_profile.get('email_verified', False)
                })

        return user

database_interface = DatabaseInterface()