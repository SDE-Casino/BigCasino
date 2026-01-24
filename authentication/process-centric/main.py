from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests
import os
import jwt
import uuid as uuid_lib

load_dotenv()

app = FastAPI(title="Process-Centric Authentication Service", description="Service for user authentication and registration")

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


def mongo_id_to_uuid(mongo_id: str) -> str:
    """
    Convert MongoDB ObjectId hex string to UUID format.
    MongoDB ObjectId is 24 hex chars, UUID is 32 hex chars with hyphens.
    We'll pad the ObjectId to 32 chars and format as UUID.
    """
    # Remove any hyphens if present
    clean_id = mongo_id.replace('-', '')

    # If it's already 24 chars (ObjectId), pad to 32 chars
    if len(clean_id) == 24:
        # Pad with zeros to make it 32 chars (UUID length)
        padded_id = clean_id + '00000000'
    elif len(clean_id) == 32:
        padded_id = clean_id
    else:
        # Fallback: just use as-is if unexpected length
        padded_id = clean_id

    # Format as UUID: 8-4-4-4-12
    uuid_str = f"{padded_id[0:8]}-{padded_id[8:12]}-{padded_id[12:16]}-{padded_id[16:20]}-{padded_id[20:32]}"

    return uuid_str


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

    # Ensure user ID is in UUID format (logic layer should already return UUIDs)
    user_id = data["id"]
    if len(user_id.replace('-', '')) == 24:
        # It's a MongoDB ObjectId, convert to UUID
        user_id = mongo_id_to_uuid(user_id)

    access_token = create_jwt(
        {
            "sub": user_id,
            "type": "access",
            "provider": "local"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": user_id,
            "type": "refresh",
            "provider": "local"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        path="/"
    )

    return {
        "id": user_id,
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

    # Ensure user ID is in UUID format (logic layer should already return UUIDs)
    user_id = data["id"]
    if len(user_id.replace('-', '')) == 24:
        # It's a MongoDB ObjectId, convert to UUID
        user_id = mongo_id_to_uuid(user_id)

    access_token = create_jwt(
        {
            "sub": user_id,
            "type": "access",
            "provider": "local"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": user_id,
            "type": "refresh",
            "provider": "local"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        path="/"
    )

    return {
        "id": user_id,
        "username": data["username"],
        "access_token": access_token
    }


@app.post("/refresh")
def refresh(request: Request):
    """
    Provide a new access token for the user (supports both local and Google providers)
    """
    token = request.cookies.get("refresh_token")
    
    # Fallback: check Authorization header for refresh token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Refresh "):
            token = auth_header[8:]  # Remove "Refresh " prefix
    
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

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    provider = payload.get("provider", "local")
    user_id = payload["sub"]

    new_access = create_jwt(
        {
            "sub": user_id,  # Already in UUID format from original token
            "type": "access",
            "provider": provider
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
        path="/"
    )
    return {"detail": "Logged out successfully"}


# =====================
# GOOGLE AUTH
# =====================

@app.get("/google/login")
def google_login():
    """
    Redirect to google service for authentication
    Use external URL for browser redirect
    """
    url = f"{os.getenv('GOOGLE_AUTH_EXTERNAL_URL') or os.getenv('GOOGLE_REDIRECT_URL')}/auth/google"
    return RedirectResponse(url=url)

@app.get("/google/callback/refresh_token")
def google_refresh_token(request: Request, response: Response):
    """
    After google service manages authentication, it calls this to provide a refresh token
    and redirects back to the UI
    """
    data = request.query_params
    mongo_user_id = data.get("id")

    # Convert MongoDB ObjectId to UUID format for PostgreSQL compatibility
    user_id = mongo_id_to_uuid(mongo_user_id)

    access_token = create_jwt(
        {
            "sub": user_id,
            "type": "access",
            "provider": "google"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    refresh_token = create_jwt(
        {
            "sub": user_id,
            "type": "refresh",
            "provider": "google"
        },
        minutes=int(os.getenv("REFRESH_TOKEN_MINUTES"))
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        path="/"
    )

    # Redirect to UI with tokens in URL fragment (hash) for client-side access
    # Using fragment (#) instead of query params for better security (not sent to server in subsequent requests)
    ui_url = os.getenv("UI_REDIRECT_URL", "http://localhost:3000/auth")
    redirect_url = f"{ui_url}#access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=redirect_url)


@app.get("/google/verify_token")
def verify_google_token(request: Request):
    """
    Verify google token, retrieve user info from google service
    Generate and return a JWT access token for UI to use with other services
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

    google_data = google_response.json()

    # Extract user ID from Google response
    # The Google service returns a JWT payload with 'user_id' and 'email'
    mongo_user_id = google_data.get("user_id") or google_data.get("id") or google_data.get("user", {}).get("id")
    username = google_data.get("email") or google_data.get("username") or google_data.get("user", {}).get("email")

    if not mongo_user_id:
        raise HTTPException(status_code=500, detail="User ID not found in Google response")

    # Convert MongoDB ObjectId to UUID format for PostgreSQL compatibility
    user_id = mongo_id_to_uuid(mongo_user_id)

    # Generate JWT access token (same as local auth)
    # Use the converted UUID (user_id) not the original MongoDB ID (mongo_user_id)
    access_token = create_jwt(
        {
            "sub": user_id,  # Use UUID format
            "type": "access",
            "provider": "google"
        },
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES"))
    )

    response_data = {
        "id": user_id,  # Return UUID format
        "username": username,
        "access_token": access_token,
        "login_type": "google"
    }

    return response_data


@app.post("/google/logout")
def google_logout(response: Response):
    """
    Logout from google service
    """
    url = f"{os.getenv('GOOGLE_REDIRECT_URL')}/auth/logout"
    return RedirectResponse(url=url)
