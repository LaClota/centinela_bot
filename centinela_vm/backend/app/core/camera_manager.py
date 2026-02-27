import cv2
import threading
import time
import yaml
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CameraConfig:
    id: str
    name: str
    source: str
    enabled: bool

class CameraStream:
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap = None
        self.last_frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.status = "offline"

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.release()

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = "offline"

    def _capture_loop(self):
        logger.info(f"Starting capture for {self.config.name}")
        while self.running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    self.status = "connecting"
                    self.cap = cv2.VideoCapture(self.config.source)
                    if not self.cap.isOpened():
                        logger.warning(f"Failed to connect to {self.config.name} at {self.config.source}")
                        self.status = "error"
                        time.sleep(5)
                        continue
                    self.status = "online"
                    logger.info(f"Connected to {self.config.name}")

                ret, frame = self.cap.read()
                if not ret:
                    logger.warning(f"Lost stream for {self.config.name}")
                    self.release()
                    continue

                with self.lock:
                    self.last_frame = frame
                
                # Limit FPS if needed to save CPU? For now, process as fast as possible or sleep
                # time.sleep(0.01) 

            except Exception as e:
                logger.error(f"Error in capture loop for {self.config.name}: {e}")
                self.release()
                time.sleep(5)

    def get_frame(self):
        with self.lock:
            if self.last_frame is None:
                return None
            return self.last_frame.copy()

class CameraManager:
    def __init__(self, config_path: str = "config/cameras.yaml"):
        self.config_path = config_path
        self.streams: Dict[str, CameraStream] = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)
                
            for cam_data in data.get('cameras', []):
                if not cam_data.get('enabled', True):
                    continue
                    
                config = CameraConfig(
                    id=cam_data['id'],
                    name=cam_data['name'],
                    source=cam_data['source'],
                    enabled=cam_data.get('enabled', True)
                )
                
                if config.id not in self.streams:
                    self.streams[config.id] = CameraStream(config)
                    self.streams[config.id].start()
                    
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. using defaults or empty.")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def get_stream(self, camera_id: str) -> Optional[CameraStream]:
        return self.streams.get(camera_id)

    def get_all_streams(self) -> List[CameraStream]:
        return list(self.streams.values())

    def stop_all(self):
        for stream in self.streams.values():
            stream.stop()

camera_manager = CameraManager()
