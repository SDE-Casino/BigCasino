from fastapi import FastAPI
from routes.register import router as register_router
from routes.login import router as login_router

app = FastAPI(title="Logic-Layer: Authentication Service", description="Handles user registration and login functionalities.")

app.include_router(login_router)
app.include_router(register_router)