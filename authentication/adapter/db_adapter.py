from fastapi import FastAPIs, HTTPException
from models import User
from pydantic import BaseModel
from cryptography import bcrypt
from sqlalchemy import create_engine, select, Session

# Create the engine that will connect to the database
# TODO: The connection string below is for testing, later must be replaced by a real database URL
DATABASE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(DATABASE_URL)

class RequestArgs(BaseModel):
    username: str
    password: str

app = FastAPIs()

@app.get("/user/{username}")
def get_user(username: str):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == username)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User {username} not found")
        else:
            return user

@app.post("/create_user")
def create_user(args: RequestArgs):
    with Session(engine) as session:
        hashed_password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=args.username, password=hashed_password)

        session.add(new_user)
        session.commit()
        return new_user

@app.post("/update_user/{username}")
def update_user(username: str, args: RequestArgs):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == username)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User {username} not found")

        user.password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt())
        session.commit()
        return user

@app.delete("/delete_user/{username}")
def delete_user(username: str):
    with Session(engine) as session:
        user = session.execute(select(User).filter(User.username == username)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User {username} not found")

        session.delete(user)
        session.commit()