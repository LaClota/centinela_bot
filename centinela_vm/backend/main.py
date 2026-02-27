from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging
import cv2
import time
from app.core.camera_manager import camera_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("centinela_vm_backend")

app = FastAPI(title="Centinela VM Core", description="Heavy processing unit for security system", version="0.1.0")

# CORS (Allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    camera_manager.load_config()
    logger.info("Camera Manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    camera_manager.stop_all()
    logger.info("Camera Manager stopped")

@app.get("/")
def read_root():
    return {"status": "online", "system": "Centinela VM Core", "cameras": len(camera_manager.get_all_streams())}

@app.get("/cameras")
def get_cameras():
    return [
        {
            "id": cam.config.id, 
            "name": cam.config.name, 
            "status": cam.status,
            "source": cam.config.source
        } 
        for cam in camera_manager.get_all_streams()
    ]

def generate_frames(camera_id: str):
    stream = camera_manager.get_stream(camera_id)
    if not stream:
        return
    
    while True:
        frame = stream.get_frame()
        if frame is not None:
            # Resize for web stream if needed to save bandwidth
            # frame = cv2.resize(frame, (640, 360))
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.1)
        time.sleep(0.05) # Cap at ~20 FPS for stream

@app.get("/cameras/{camera_id}/stream")
def video_feed(camera_id: str):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")
