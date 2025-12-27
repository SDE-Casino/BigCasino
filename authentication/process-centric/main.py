from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests
import os
import jwt

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# MODELS
# =====================

class UserCredentials(BaseModel):
    username: str
    password: str


# =====================
# HELPERS
# =====================

def create_jwt(payload: dict, minutes: int):
    data = payload.copy()
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)

    return jwt.encode(
        data,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )


def logic_post(path: str, json: dict):
    url = f"{os.getenv('LOGIC_LAYER_URL')}{path}"
    response = requests.post(url, json=json)
    return response


# =====================
# LOCAL AUTH
# =====================

@app.post("/register")
def register(credentials: UserCredentials, response: Response):
    """
    Register user with username and password
    """
    logic_response = logic_post("/register", credentials.dict())

    if logic_response.status_code != 200:
        raise HTTPException(
            status_code=logic_response.status_code,
            detail=logic_response.json().get("detail", "Registration failed")
        )

    data = logic_response.json()

    access_token = create_jwt(
        {
            "sub": data["id"],
            "type": "access",
            "provider": "local"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": data["id"],
            "type": "refresh",
            "provider": "local"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/refresh"
    )

    return {
        "id": data["id"],
        "username": data["username"],
        "access_token": access_token
    }

@app.post("/login")
def login(credentials: UserCredentials, response: Response):
    """
    Login user with username and password
    """
    logic_response = logic_post("/login", credentials.dict())

    if logic_response.status_code != 200:
        raise HTTPException(
            status_code=logic_response.status_code,
            detail=logic_response.json().get("detail", "Login failed")
        )

    data = logic_response.json()

    access_token = create_jwt(
        {
            "sub": data["id"],
            "type": "access",
            "provider": "local"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": data["id"],
            "type": "refresh",
            "provider": "local"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/refresh"
    )

    return {
        "id": data["id"],
        "username": data["username"],
        "access_token": access_token
    }


@app.post("/refresh")
def refresh(request: Request):
    """
    Provide a new access token for the user
    """
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    if payload.get("type") != "refresh" or payload.get("provider") != "local":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_jwt(
        {
            "sub": payload["sub"],
            "type": "access",
            "provider": "local"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    return {"access_token": new_access}


@app.post("/logout")
def logout(response: Response):
    """
    Logout user by deleting refresh token cookie
    """
    response.delete_cookie(
        key="refresh_token",
        path="/refresh"
    )
    return {"detail": "Logged out successfully"}


# =====================
# GOOGLE AUTH
# =====================

@app.get("/google/login")
def google_login():
    """
    Redirect to google service for authentication
    """
    url = f"{os.getenv('GOOGLE_REDIRECT_URL')}/auth/google"
    return RedirectResponse(url=url)

@app.get("/google/callback/refresh_token")
def google_refresh_token(request: Request, response: Response):
    """
    After google service manages authentication, it calls this to provide a refresh token
    """
    data = request.query_params
    access_token = create_jwt(
        {
            "sub": data["id"],
            "type": "access",
            "provider": "google"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": data["id"],
            "type": "refresh",
            "provider": "google"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/refresh"
    )

    return {
        "id": data["id"],
        "username": data["username"],
        "access_token": access_token
    }


@app.get("/google/verify_token")
def verify_google_token(request: Request):
    """
    Verify google token, retrieve user info from google service
    """
    url = f"{os.getenv('GOOGLE_AUTH_URL')}/auth/verify"

    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["authorization"] = auth
    auth_cookie = request.cookies.get("authToken")
    if auth_cookie:
        headers["cookie"] = f"authToken={auth_cookie}"

    google_response = requests.get(url, headers=headers)

    if google_response.status_code != 200:
        raise HTTPException(
            status_code=google_response.status_code,
            detail="Invalid Google token"
        )

    return {
        "login_type": "google",
        **google_response.json()
    }


@app.post("/google/logout")
def google_logout(response: Response):
    """
    Logout from google service
    """
    url = f"{os.getenv('GOOGLE_REDIRECT_URL')}/auth/logout"
    return RedirectResponse(url=url)
