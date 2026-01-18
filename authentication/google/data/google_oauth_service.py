from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
import os

class GoogleOAuthService:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/userinfo.email',
                'openid'
            ]
        )
        self.flow.redirect_uri = self.redirect_uri

    def get_auth_url(self) -> str:
        """
        Generates the Google authorization URL
        """
        authorization_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state

    def verify_token(self, token: str) -> dict:
        """
        Verifies received Google token's ID
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.client_id
            )
            return idinfo
        except ValueError as e:
            raise Exception(f"Token non valido: {str(e)}")

    def get_credentials_from_code(self, code: str):
        """
        Get credentials from authorization code
        """
        self.flow.fetch_token(code=code)
        return self.flow.credentials

    def get_user_info(self, credentials) -> dict:
        """
        Get user info from credentials
        """
        return id_token.verify_oauth2_token(
            credentials.id_token,
            requests.Request(),
            self.client_id
        )

google_oauth_service = GoogleOAuthService()