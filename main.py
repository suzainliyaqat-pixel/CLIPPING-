
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

app = FastAPI(title="CLIPPER AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("/tmp/clipper_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

jobs = {}


@app.get("/")
def home():
    return {
        "app": "CLIPPER",
        "status": "Backend running",
        "features": [
            "Video upload",
            "YouTube link submission",
            "Job status checking"
        ],
        "message": "Welcome to CLIPPER AI"
    }


@app.post("/upload")
async def upload_video(video: UploadFile = File(...)):

    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid video file."
        )

    job_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{job_id}_{Path(video.filename).name}"

    total_size = 0

    try:
        with file_path.open("wb") as output:
            while True:
                chunk = await video.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Maximum upload size is 100 MB."
                    )

                output.write(chunk)

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    finally:
        await video.close()

    jobs[job_id] = {
        "job_id": job_id,
        "source": "upload",
        "filename": video.filename,
        "status": "received_not_processed"
    }

    return {
        "job_id": job_id,
        "status": "received_not_processed",
        "message": "Video received successfully. AI clipping engine is not connected yet."
    }


@app.post("/youtube")
def submit_youtube_link(data: dict):

    url = data.get("url", "").strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a YouTube URL."
        )

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    allowed_hosts = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be"
    }

    if parsed.scheme not in ("http", "https") or host not in allowed_hosts:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid YouTube URL."
        )

    job_id = str(uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "source": "youtube",
        "url": url,
        "status": "received_not_processed"
    }

    return {
        "job_id": job_id,
        "status": "received_not_processed",
        "message": "YouTube link received. Video has not been downloaded or processed."
    }


@app.get("/status/{job_id}")
def get_status(job_id: str):

    job = jobs.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return job
