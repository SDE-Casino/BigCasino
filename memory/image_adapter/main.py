from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Image Adapter API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Image Adapter API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/images")
def get_images():
    """
    Endpoint to get available images
    """
    # This is a placeholder implementation
    return {"images": []}

@app.post("/images/process")
def process_image():
    """
    Endpoint to process an image
    """
    # This is a placeholder implementation
    return {"message": "Image processing endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)