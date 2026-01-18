from business.auth_business_logic import auth_business_logic
from data.google_oauth_service import google_oauth_service

class AuthenticationService:
    def __init__(self):
        self.auth_logic = auth_business_logic
        self.google_service = google_oauth_service

    def initiate_google_auth(self) -> tuple:
        """
        Starts Google autjentication process
        """
        return self.google_service.get_auth_url()

    def handle_google_callback(self, code: str) -> dict:
        """
        Handles Google callback
        """
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
        """
        Direct authentication through Google token
        """
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
        """
        Verify session token
        """
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