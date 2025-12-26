from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import requests
import os

class RequestArgs(BaseModel):
    username: str
    password: str

router = APIRouter()

@router.post("/login")
def login_user(user: RequestArgs):
    """
    Endpoint to login an existing user in the system
    """
    url = os.getenv("ADAPTER_URL")
    response = requests.post(f"{url}/validate_credentials", json=user.dict())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()