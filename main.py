from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CLIPPER AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "app": "CLIPPER",
        "status": "Backend running",
        "message": "Welcome to CLIPPER AI"
    }

@app.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    if not video.content_type or not video.content_type.startswith("video/"):
        return {"error": "Please upload a video file"}

    return {
        "filename": video.filename,
        "status": "Video received",
        "message": "AI processing engine is not connected yet"
    }
