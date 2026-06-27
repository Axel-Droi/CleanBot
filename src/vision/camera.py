import cv2
import numpy as np


class Camera:
    """Generic USB / webcam via OpenCV."""

    def __init__(self, index: int = 0, width: int = 1280, height: int = 720):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {index}")

    def read(self) -> np.ndarray:
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Failed to read frame from camera")
        return frame

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.release()


try:
    import pyrealsense2 as rs

    class RealSenseCamera:
        """Intel RealSense D4xx — aligned color + depth streams."""

        def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
            self.pipeline = rs.pipeline()
            cfg = rs.config()
            cfg.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            cfg.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
            self.pipeline.start(cfg)
            self.align = rs.align(rs.stream.color)

        def read(self) -> tuple[np.ndarray, np.ndarray]:
            """Returns (color_bgr, depth_uint16) aligned to the color frame."""
            frames = self.pipeline.wait_for_frames()
            aligned = self.align.process(frames)
            color = np.asanyarray(aligned.get_color_frame().get_data())
            depth = np.asanyarray(aligned.get_depth_frame().get_data())
            return color, depth

        def depth_at(self, depth_frame: np.ndarray, x: int, y: int) -> float:
            """Returns distance in meters at pixel (x, y)."""
            return float(depth_frame[y, x]) * 0.001  # mm → m

        def release(self):
            self.pipeline.stop()

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.release()

except ImportError:
    pass  # pyrealsense2 not installed — RealSenseCamera unavailable
