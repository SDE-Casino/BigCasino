from business.auth_business_logic import auth_business_logic
from data.google_oauth_service import google_oauth_service

class AuthenticationService:
    def __init__(self):
        self.auth_logic = auth_business_logic
        self.google_service = google_oauth_service

    def initiate_google_auth(self) -> tuple:
        """Inizia processo di autenticazione Google"""
        return self.google_service.get_auth_url()

    def handle_google_callback(self, code: str) -> dict:
        """Gestisce il callback da Google"""
        try:
            result = self.auth_logic.login_with_google_code(code)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def authenticate_with_google_token(self, google_token: str) -> dict:
        """Autenticazione diretta con token Google"""
        try:
            result = self.auth_logic.login_with_google(google_token)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def verify_session_token(self, token: str) -> dict:
        """Verifica token di sessione"""
        try:
            payload = self.auth_logic.verify_jwt_token(token)
            return {
                'success': True,
                'data': payload
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

authentication_service = AuthenticationService()