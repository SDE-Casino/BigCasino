from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import requests
import os

class RequestArgs(BaseModel):
    username: str
    password: str

router = APIRouter()

@router.post("/register")
def register_user(user: RequestArgs):
    """
    Endpoint to register a new user in the system
    """
    url = os.getenv("ADAPTER_URL")
    response = requests.post(f"{url}/create_user", json=user.dict())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()

@router.post("/new_password/{user_id}")
def update_user(user_id: str, password: str):
    """
    Endpoint to update an existing user in the system
    """
    url = os.getenv("ADAPTER_URL")

    args = {
        'password': password
    }
    response = requests.post(f"{url}/update_user/{user_id}", json=args)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()

@router.delete("/delete/{user_id}")
def delete_user(user_id: str):
    """
    Endpoint to delete existing user in the system
    """
    url = os.getenv("ADAPTER_URL")
    response = requests.post(f"{url}/delete_user/{user_id}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    return response.json()