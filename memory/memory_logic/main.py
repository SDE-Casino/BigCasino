from fastapi import FastAPI

app = FastAPI(title="Memory Logic Service", description="A simple FastAPI service for memory logic operations")

@app.get("/")
async def root():
    return {"message": "Memory Logic Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}