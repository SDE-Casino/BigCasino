from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from PIL import Image
import io
import base64

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

def getBase64Image():
    """
    Downloads an image from cataas.com with width 1280px,
    crops it to height 720px, and returns the base64 encoded image.
    """
    try:
        image_url = "https://cataas.com/cat?width=1280"
        response = requests.get(image_url)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        
        width, height = img.size
        target_height = 720
        
        # Calculate the top-left corner for cropping (centered)
        top = (height - target_height) // 2 if height > target_height else 0
        bottom = top + target_height if height > target_height else height
        
        if height > target_height:
            cropped_img = img.crop((0, top, width, bottom))
        else:
            cropped_img = img
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if cropped_img.mode != 'RGB':
            cropped_img = cropped_img.convert('RGB')
        
        buffer = io.BytesIO()
        cropped_img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

@app.get("/image/base64")
def get_image_base64():
    """
    Endpoint to get a base64 encoded cat image from cataas.com
    with dimensions 1280x720.
    """
    try:
        base64_image = getBase64Image()
        return {"image": base64_image}
        # return {"image": "placeholder"}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)