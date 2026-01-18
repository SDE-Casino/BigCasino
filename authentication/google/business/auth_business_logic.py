from data.google_oauth_service import google_oauth_service
from adapters.database_interface import database_interface
import jwt
import os
from datetime import datetime, timedelta

class AuthBusinessLogic:
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
        self.jwt_algorithm = 'HS256'
        self.token_expiry_days = 7

    def _generate_jwt_token(self, user: dict) -> str:
        """
        Generates JWT token for the user
        """
        payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'exp': datetime.now() + timedelta(days=self.token_expiry_days),
            'iat': datetime.now()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_jwt_token(self, token: str) -> dict:
        """Verifica JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token scaduto")
        except jwt.InvalidTokenError:
            raise Exception("Token non valido")

    def login_with_google(self, google_token: str) -> dict:
        """
        Login with Google token
        """
        google_profile = google_oauth_service.verify_token(google_token)
        user = database_interface.find_or_create_user_from_google(google_profile)

        # Generate JWT
        session_token = self._generate_jwt_token(user)

        user_dict = {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'picture': user.get('picture')
        }

        return {
            'user': user_dict,
            'token': session_token
        }

    def login_with_google_code(self, code: str) -> dict:
        """
        Login with Google authorization code
        """
        credentials = google_oauth_service.get_credentials_from_code(code)

        google_profile = google_oauth_service.get_user_info(credentials)

        user = database_interface.find_or_create_user_from_google(google_profile)

        # Generate JWT
        session_token = self._generate_jwt_token(user)

        user_dict = {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'picture': user.get('picture')
        }

        return {
            'user': user_dict,
            'token': session_token
        }

auth_business_logic = AuthBusinessLogic()