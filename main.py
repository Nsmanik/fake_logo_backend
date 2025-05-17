from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.predict import predict_logo
import shutil
import os
import uuid

app = FastAPI(title="Fake Logo Detector API")

# Allow frontend calls (camera/gallery)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/scan-logo/")
async def scan_logo(image: UploadFile = File(...), brand: str = Form("Unknown")):
    try:
        # Save the uploaded image temporarily
        temp_filename = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.jpg")
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Call prediction logic
        verdict, confidence = predict_logo(temp_filename)

        # Delete temp file
        os.remove(temp_filename)

        return JSONResponse(content={
            "brand": brand,
            "verdict": verdict,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    return {"message": "Fake Logo Detector API is running!"}