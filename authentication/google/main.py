from fastapi import FastAPI, HTTPException, Response, Cookie, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from process.authentication_service import authentication_service
from typing import Optional

app = FastAPI()

class GoogleTokenRequest(BaseModel):
    googleToken: str

@app.get('/auth/google')
async def google_auth():
    """Inizia autenticazione Google"""
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
        # TODO: Redirect to frontend URL
        response = RedirectResponse(url='/dashboard')
        response.set_cookie(
            key='authToken',
            value=result['data']['token'],
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=7*24*60*60
        )
        return response
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.post('/auth/google/token')
async def google_token_auth(request: GoogleTokenRequest):
    """Autenticazione diretta con token Google"""
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
    """Verifica token di sessione"""
    token = authToken or (authorization.replace('Bearer ', '') if authorization else None)

    if not token:
        raise HTTPException(status_code=401, detail="Token mancante")

    result = authentication_service.verify_session_token(token)

    if result['success']:
        return result['data']
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.post('/auth/logout')
async def logout(response: Response):
    """Logout"""
    response.delete_cookie('authToken')
    return {'message': 'Logout effettuato'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)