from fastapi import FastAPI, HTTPException
from models.users import User, Base
from pydantic import BaseModel
import bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# TODO: The connection string below is for testing, later must be replaced by a real database URL
DATABASE_URL = "sqlite+pysqlite:///./test.db"

# Create the engine that will connect to the database
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

class RequestArgs(BaseModel):
    username: str
    password: str

app = FastAPI()

@app.get("/user_name/{id}")
def get_user_name(id: str):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.id == id)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with id '{id}' not found")
        else:
            return user.username

@app.get("/user_id/{username}")
def get_user_id(username: str):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == username)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User {username} not found")
        else:
            return user.id

@app.post("/create_user")
def create_user(args: RequestArgs):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == args.username)).scalar_one_or_none()
        if user:
            raise HTTPException(status_code=409, detail=f"Username '{args.username}' is already taken")

        hashed_password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=args.username, password=hashed_password)

        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'username': new_user.username
        }

@app.post("/update_user/{user_id}")
def update_user(user_id: str, args: RequestArgs):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

        user.password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt())
        session.commit()
        return user

@app.delete("/delete_user/{user_id}")
def delete_user(user_id: str):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

        session.delete(user)
        session.commit()

        return {"detail": f"User with id {user_id} deleted successfully"}

@app.post("/validate_credentials")
def validate_credentials(args: RequestArgs):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == args.username)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Invalid username or password")

        if not bcrypt.checkpw(args.password.encode('utf-8'), user.password):
            raise HTTPException(status_code=404, detail="Invalid username or password")

        return {
            'id': user.id,
            'username': user.username
        }