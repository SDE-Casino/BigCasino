from fastapi import FastAPI, HTTPException, Response, Cookie, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from process.authentication_service import authentication_service
from typing import Optional
import os

app = FastAPI(title="Google Authentication Adapter", description="Handles Google OAuth2 authentication.")

class GoogleTokenRequest(BaseModel):
    googleToken: str

@app.get('/auth/google')
async def google_auth():
    """
    Google authentication entrypoint
    """
    auth_url, _ = authentication_service.initiate_google_auth()
    return RedirectResponse(url=auth_url)

@app.get('/auth/google/callback')
async def google_callback(code: str, response: Response):
    """
    Endpoint called from google after verifying the user
    Callback da Google
    """
    if not code:
        raise HTTPException(status_code=400, detail="Codice mancante")

    result = authentication_service.handle_google_callback(code)

    if result['success']:
        url = os.getenv("IDP_URL") + f"/google/callback/refresh_token?id={result['data']['user']['id']}&username={result['data']['user']['email']}"
        return RedirectResponse(url=url)
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.post('/auth/google/token')
async def google_token_auth(request: GoogleTokenRequest):
    """
    Direct authentication through Google token
    """
    result = authentication_service.authenticate_with_google_token(request.googleToken)

    if result['success']:
        return result['data']
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.get('/auth/verify')
async def verify_token(
    authToken: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """
    Verify session token
    """
    token = authToken or (authorization.replace('Bearer ', '') if authorization else None)

    if not token:
        raise HTTPException(status_code=401, detail="Token mancante")

    result = authentication_service.verify_session_token(token)

    if result['success']:
        return result['data']
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.post('/auth/logout')
async def logout():
    """Logout"""
    return {'message': 'Logout effettuato'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)