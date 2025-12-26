from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os
import jwt

load_dotenv()


app = FastAPI()

class UserCredentials(BaseModel):
    username: str
    password: str

# Helper functions
def create_jwt(payload: dict, minutes: int):
    data = payload.copy()
    data["exp"] = datetime.now() + timedelta(minutes=minutes)
    return jwt.encode(
        data,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )

@app.post("/register")
def register(credentials: UserCredentials, response: Response):
    """
    Endpoint for registering a new user
    """
    url = os.getenv("LOGIC_LAYER_URL") + "/register"
    logic_response = requests.post(url, json=credentials.dict())

    if logic_response.status_code != 200:
        raise HTTPException(
            status_code=logic_response.status_code,
            detail=logic_response.json()['detail']
        )

    data = logic_response.json()

    # --- ACCESS TOKEN (breve) ---
    access_token = create_jwt(
        {
            "sub": data["id"],
            "type": "access"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    # --- REFRESH TOKEN (lungo) ---
    refresh_token = create_jwt(
        {
            "sub": data["id"],
            "type": "refresh"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    # --- COOKIE HttpOnly ---
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,      # False solo in dev locale
        samesite="lax",
        path="/refresh"  # solo endpoint refresh
    )

    # --- RESPONSE BODY ---
    return {
        "id": data["id"],
        "username": data["username"],
        "access_token": access_token
    }

@app.post("/refresh")
def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    print(token)

    try:
        print("PRIMA")
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        print("DOPO")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh expired")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token")

    new_access = create_jwt(
        {
            "sub": payload["sub"],
            "type": "access"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    return {"access_token": new_access}

@app.post("/login")
def login(credentials: UserCredentials, response: Response):
    """
    Endpoint for user login
    """
    url = os.getenv("LOGIC_LAYER_URL") + "/login"
    logic_response = requests.post(url, json=credentials.dict())

    if logic_response.status_code != 200:
        raise HTTPException(
            status_code=logic_response.status_code,
            detail=logic_response.json()['detail']
        )

    data = logic_response.json()

    # --- ACCESS TOKEN (breve) ---
    access_token = create_jwt(
        {
            "sub": data["id"],
            "type": "access"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    # --- REFRESH TOKEN (lungo) ---
    refresh_token = create_jwt(
        {
            "sub": data["id"],
            "type": "refresh"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    # --- COOKIE HttpOnly ---
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/refresh"
    )

    # --- RESPONSE BODY ---
    return {
        "id": data["id"],
        "username": data["username"],
        "access_token": access_token
    }

@app.post("/logout")
def logout(response: Response):
    """
    Endpoint for user logout
    """
    response.delete_cookie(
        key="refresh_token",
        path="/refresh"
    )
    return {"detail": "Logged out successfully"}