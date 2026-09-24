#!/usr/bin/env python3
"""Real-time object detection and tracking for vehicles and people.

This module provides enhanced traffic and people counting using YOLOv8.
Supports webcam, direct URLs, and YouTube streams with multi-line detection,
advanced tracking, and automatic photo capture.
"""

import json
import logging
import math
import os
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Configuration constants
YOLO_MODEL: str = "yolov8n.pt"
DEFAULT_SAVE_DIR: str = "traffic_people_photos"
CONFIDENCE_THRESHOLD: float = 0.3
MAX_DISAPPEARED_FRAMES: int = 30
MAX_TRACKING_DISTANCE: int = 100
LINE_CROSSING_TOLERANCE: int = 25
MIN_TIME_BETWEEN_CAPTURES: float = 0.5
BUFFER_SIZE: int = 1
OPTIMAL_FPS: int = 30
OPTIMAL_WIDTH: int = 1280
OPTIMAL_HEIGHT: int = 720

VEHICLE_CLASSES: List[str] = ["car", "truck", "bus", "motorcycle", "bicycle"]
PEOPLE_CLASSES: List[str] = ["person"]

COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "car": (0, 255, 0),
    "truck": (255, 0, 0),
    "bus": (0, 0, 255),
    "motorcycle": (255, 255, 0),
    "bicycle": (255, 255, 0),
    "person": (255, 0, 255),
}


class EnhancedTrafficPeopleCounter:
    """Enhanced real-time traffic and people counter with advanced tracking."""

    def __init__(
        self, save_directory: str = DEFAULT_SAVE_DIR, video_url: Optional[str] = None
    ) -> None:
        """Initialize the counter.

        Args:
            save_directory (str): Directory to save detection photos.
            video_url (Optional[str]): Video source URL or None for webcam.
        """
        logger.info("Initializing Enhanced Traffic & People Counter")
        self.yolo_model: YOLO = YOLO(YOLO_MODEL)

        self.save_directory: str = save_directory
        os.makedirs(save_directory, exist_ok=True)

        # Vehicle counts
        self.car_count: int = 0
        self.truck_count: int = 0
        self.bus_count: int = 0
        self.motorcycle_count: int = 0

        # People count
        self.people_count: int = 0

        # Tracking system
        self.object_tracker: Dict[int, Dict[str, Any]] = {}
        self.crossed_objects: Set[str] = set()
        self.object_id_counter: int = 0

        # Statistics
        self.total_vehicles: int = 0
        self.total_people: int = 0
        self.photos_saved: int = 0
        self.start_time: float = time.time()
        self.last_crossing_time: float = 0

        # Performance
        self.frame_count: int = 0
        self.fps_history: Deque[float] = deque(maxlen=30)

        # Detection lines
        self.counting_lines: List[Dict[str, Any]] = []

        # Video source
        self.video_url: Optional[str] = video_url

        self.load_statistics()
        logger.info("Counter initialized successfully")

    def load_statistics(self) -> None:
        """Load previous statistics from file."""
        stats_file = os.path.join(self.save_directory, "enhanced_stats.json")
        if not os.path.exists(stats_file):
            return

        try:
            with open(stats_file, "r") as f:
                stats = json.load(f)
                self.car_count = stats.get("car_count", 0)
                self.truck_count = stats.get("truck_count", 0)
                self.bus_count = stats.get("bus_count", 0)
                self.motorcycle_count = stats.get("motorcycle_count", 0)
                self.people_count = stats.get("people_count", 0)
                self.total_vehicles = stats.get("total_vehicles", 0)
                self.total_people = stats.get("total_people", 0)
                self.photos_saved = stats.get("photos_saved", 0)
                logger.info(
                    f"Loaded stats: {self.total_vehicles} vehicles, "
                    f"{self.total_people} people"
                )
        except Exception as e:
            logger.warning(f"Could not load statistics: {e}")

    def save_statistics(self) -> None:
        """Save current statistics to file."""
        stats = {
            "car_count": self.car_count,
            "truck_count": self.truck_count,
            "bus_count": self.bus_count,
            "motorcycle_count": self.motorcycle_count,
            "people_count": self.people_count,
            "total_vehicles": self.total_vehicles,
            "total_people": self.total_people,
            "photos_saved": self.photos_saved,
            "session_duration": time.time() - self.start_time,
            "last_updated": datetime.now().isoformat(),
        }

        stats_file = os.path.join(self.save_directory, "enhanced_stats.json")
        try:
            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save statistics: {e}")

    def setup_counting_lines(self, frame_shape: Tuple[int, int, int]) -> None:
        """Setup multiple counting lines.

        Args:
            frame_shape (Tuple[int, int, int]): Frame dimensions (H, W, C).
        """
        h, w = frame_shape[:2]
        self.counting_lines = [
            {"y": int(h * 0.4), "name": "Entry Line", "color": (0, 255, 255)},
            {"y": int(h * 0.6), "name": "Main Count Line", "color": (255, 0, 255)},
            {"y": int(h * 0.8), "name": "Exit Line", "color": (255, 255, 0)},
        ]

    def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in frame using YOLO.

        Args:
            frame (np.ndarray): Input frame.

        Returns:
            List[Dict[str, Any]]: Detected objects with metadata.
        """
        results = self.yolo_model(frame, verbose=False)[0]
        detected_objects: List[Dict[str, Any]] = []

        if results.boxes is None:
            return detected_objects

        boxes = results.boxes
        xyxy = boxes.xyxy.cpu().numpy()
        confidence = boxes.conf.cpu().numpy()
        class_ids = boxes.cls.cpu().numpy().astype(int)

        for box, conf, class_id in zip(xyxy, confidence, class_ids):
            if conf <= CONFIDENCE_THRESHOLD:
                continue

            class_name = self.yolo_model.names[class_id]
            if class_name not in VEHICLE_CLASSES + PEOPLE_CLASSES:
                continue

            center_x = (box[0] + box[2]) / 2
            center_y = (box[1] + box[3]) / 2
            width = box[2] - box[0]
            height = box[3] - box[1]
            area = width * height

            detected_objects.append(
                {
                    "box": box,
                    "confidence": conf,
                    "class_name": class_name,
                    "center_x": center_x,
                    "center_y": center_y,
                    "width": width,
                    "height": height,
                    "area": area,
                }
            )

        return detected_objects

    @staticmethod
    def calculate_distance(point1: Tuple[float, float],
                          point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points.

        Args:
            point1 (Tuple[float, float]): First point.
            point2 (Tuple[float, float]): Second point.

        Returns:
            float: Distance between points.
        """
        return math.sqrt(
            (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
        )

    def update_tracker(
        self, detected_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update object tracking with ID persistence.

        Args:
            detected_objects (List[Dict[str, Any]]): Newly detected objects.

        Returns:
            List[Dict[str, Any]]: Updated tracked objects.
        """
        current_time = time.time()

        # Mark disappeared objects
        objects_to_remove: List[int] = []
        for obj_id in self.object_tracker.keys():
            self.object_tracker[obj_id]["disappeared"] += 1
            if (
                self.object_tracker[obj_id]["disappeared"]
                > MAX_DISAPPEARED_FRAMES
            ):
                objects_to_remove.append(obj_id)

        for obj_id in objects_to_remove:
            del self.object_tracker[obj_id]

        if not detected_objects:
            return list(self.object_tracker.values())

        if not self.object_tracker:
            for obj in detected_objects:
                self._register_object(obj)
            return list(self.object_tracker.values())

        # Match detections to existing trackers
        input_centroids = [
            (obj["center_x"], obj["center_y"]) for obj in detected_objects
        ]
        object_centroids = [
            (
                self.object_tracker[obj_id]["center_x"],
                self.object_tracker[obj_id]["center_y"],
            )
            for obj_id in self.object_tracker.keys()
        ]

        distances = np.linalg.norm(
            np.array(input_centroids)[:, np.newaxis]
            - np.array(object_centroids),
            axis=2,
        )

        rows = distances.min(axis=1).argsort()
        cols = distances.argmin(axis=1)[rows]

        used_rows: Set[int] = set()
        used_cols: Set[int] = set()

        object_ids = list(self.object_tracker.keys())
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if distances[row, col] <= MAX_TRACKING_DISTANCE:
                obj_id = object_ids[col]
                obj = detected_objects[row]

                self.object_tracker[obj_id].update(
                    {
                        "center_x": obj["center_x"],
                        "center_y": obj["center_y"],
                        "box": obj["box"],
                        "confidence": obj["confidence"],
                        "disappeared": 0,
                        "last_seen": current_time,
                    }
                )

                used_rows.add(row)
                used_cols.add(col)

        unused_rows = set(range(distances.shape[0])).difference(used_rows)
        for row in unused_rows:
            self._register_object(detected_objects[row])

        return list(self.object_tracker.values())

    def _register_object(self, obj: Dict[str, Any]) -> None:
        """Register a new object for tracking.

        Args:
            obj (Dict[str, Any]): Object detection data.
        """
        self.object_tracker[self.object_id_counter] = {
            "id": self.object_id_counter,
            "class_name": obj["class_name"],
            "center_x": obj["center_x"],
            "center_y": obj["center_y"],
            "box": obj["box"],
            "confidence": obj["confidence"],
            "disappeared": 0,
            "crossed_lines": set(),
            "path": deque(maxlen=10),
            "first_seen": time.time(),
            "last_seen": time.time(),
        }
        self.object_tracker[self.object_id_counter]["path"].append(
            (obj["center_x"], obj["center_y"])
        )
        self.object_id_counter += 1

    def check_line_crossings(
        self, tracked_objects: List[Dict[str, Any]], frame: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Check for line crossings and count detections.

        Args:
            tracked_objects (List[Dict[str, Any]]): Tracked objects.
            frame (np.ndarray): Current frame for photo saving.

        Returns:
            List[Dict[str, Any]]: Recent crossings.
        """
        crossings: List[Dict[str, Any]] = []
        current_time = time.time()

        for obj in tracked_objects:
            obj_id = obj["id"]
            center_y = obj["center_y"]

            for line_idx, line in enumerate(self.counting_lines):
                line_y = line["y"]
                line_name = line["name"]
                distance_to_line = abs(center_y - line_y)

                if distance_to_line >= LINE_CROSSING_TOLERANCE:
                    continue

                crossing_key = f"{obj_id}_{line_idx}"
                if crossing_key in self.crossed_objects:
                    continue

                # Verify direction using path history
                if len(obj["path"]) >= 2:
                    prev_y = obj["path"][-2][1]
                    curr_y = obj["path"][-1][1]
                    direction = "down" if curr_y > prev_y else "up"

                    # Count only on main line to avoid duplication
                    if line_name == "Main Count Line":
                        self.crossed_objects.add(crossing_key)
                        self._count_crossing(obj, direction)
                        crossings.append(
                            {
                                "object": obj,
                                "line": line,
                                "direction": direction,
                                "timestamp": current_time,
                            }
                        )

                        # Save photo if time threshold met
                        if (
                            current_time - self.last_crossing_time
                            > MIN_TIME_BETWEEN_CAPTURES
                        ):
                            self._save_detection_photo(
                                frame, obj, line_name, direction
                            )
                            self.last_crossing_time = current_time

            obj["path"].append((obj["center_x"], obj["center_y"]))

        return crossings

    def _count_crossing(self, obj: Dict[str, Any], direction: str) -> None:
        """Count crossing based on object type.

        Args:
            obj (Dict[str, Any]): Detected object.
            direction (str): Direction of crossing.
        """
        class_name = obj["class_name"]

        if class_name in VEHICLE_CLASSES:
            if class_name == "car":
                self.car_count += 1
            elif class_name == "truck":
                self.truck_count += 1
            elif class_name == "bus":
                self.bus_count += 1
            else:
                self.motorcycle_count += 1

            self.total_vehicles += 1
            logger.info(
                f"{class_name.title()} crossed ({direction}). "
                f"Vehicles: {self.total_vehicles}"
            )

        elif class_name in PEOPLE_CLASSES:
            self.people_count += 1
            self.total_people += 1
            logger.info(
                f"Person crossed ({direction}). People: {self.total_people}"
            )

    def _save_detection_photo(
        self, frame: np.ndarray, obj: Dict[str, Any],
        line_name: str, direction: str
    ) -> None:
        """Save detection photo when object crosses line.

        Args:
            frame (np.ndarray): Current frame.
            obj (Dict[str, Any]): Detected object.
            line_name (str): Line name.
            direction (str): Crossing direction.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        class_name = obj["class_name"]
        confidence = obj["confidence"]

        filename = (
            f"{class_name}_{direction}_{timestamp}_conf{confidence:.2f}.jpg"
        )
        filepath = os.path.join(self.save_directory, filename)

        try:
            save_frame = frame.copy()
            box = obj["box"].astype(int)
            x1, y1, x2, y2 = box

            color = COLOR_MAP.get(class_name, (0, 255, 0))
            cv2.rectangle(save_frame, (x1, y1), (x2, y2), color, 2)

            label = f"{class_name} {confidence:.2f} {direction}"
            cv2.putText(
                save_frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

            cv2.imwrite(filepath, save_frame)
            self.photos_saved += 1
            logger.info(f"Saved detection photo: {filename}")
        except Exception as e:
            logger.error(f"Failed to save photo: {e}")

    def draw_enhanced_interface(
        self,
        frame: np.ndarray,
        tracked_objects: List[Dict[str, Any]],
        crossings: List[Dict[str, Any]],
    ) -> None:
        """Draw monitoring interface on frame.

        Args:
            frame (np.ndarray): Frame to draw on.
            tracked_objects (List[Dict[str, Any]]): Tracked objects.
            crossings (List[Dict[str, Any]]): Recent crossings.
        """
        h, w = frame.shape[:2]

        if not self.counting_lines:
            self.setup_counting_lines(frame.shape)

        # Draw lines
        for line in self.counting_lines:
            y = line["y"]
            color = line["color"]
            name = line["name"]

            cv2.line(frame, (0, y), (w, y), color, 2)
            cv2.putText(
                frame, name, (10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

        # Draw tracked objects
        for obj in tracked_objects:
            box = obj["box"].astype(int)
            class_name = obj["class_name"]
            confidence = obj["confidence"]
            obj_id = obj["id"]

            x1, y1, x2, y2 = box
            color = COLOR_MAP.get(class_name, (0, 255, 0))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            label = f"ID:{obj_id} {class_name} {confidence:.2f}"
            cv2.putText(
                frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

            # Draw path
            if len(obj["path"]) > 1:
                points = np.array(obj["path"], np.int32)
                cv2.polylines(frame, [points], False, color, 1)

        # Highlight recent crossings
        for crossing in crossings:
            obj = crossing["object"]
            box = obj["box"].astype(int)
            x1, y1, x2, y2 = box

            cv2.putText(
                frame,
                f"CROSSED! {crossing['direction'].upper()}",
                (x1, y2 + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

        self._draw_statistics_panel(frame)

    def _draw_statistics_panel(self, frame: np.ndarray) -> None:
        """Draw statistics panel on frame.

        Args:
            frame (np.ndarray): Frame to draw on.
        """
        panel_height, panel_width = 280, 400
        info_panel = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
        info_panel.fill(50)

        y_offset = 25
        line_height = 22

        # Title
        cv2.putText(
            info_panel,
            "ENHANCED TRAFFIC & PEOPLE COUNTER",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        y_offset += line_height + 5

        # Vehicles section
        cv2.putText(
            info_panel, "VEHICLES:", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1
        )
        y_offset += line_height

        stats = [
            (f"  Cars: {self.car_count}", (0, 255, 0)),
            (f"  Trucks: {self.truck_count}", (255, 0, 0)),
            (f"  Buses: {self.bus_count}", (0, 0, 255)),
            (f"  Motorcycles/Bikes: {self.motorcycle_count}", (255, 255, 0)),
        ]

        for text, color in stats:
            cv2.putText(
                info_panel, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1
            )
            y_offset += line_height - 5

        cv2.putText(
            info_panel,
            f"  Total Vehicles: {self.total_vehicles}",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        y_offset += line_height + 5

        # People section
        cv2.putText(
            info_panel, "PEOPLE:", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1
        )
        y_offset += line_height

        cv2.putText(
            info_panel,
            f"  Total People: {self.people_count}",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 255),
            2,
        )
        y_offset += line_height + 5

        # Session stats
        session_time = int(time.time() - self.start_time)
        session_stats = [
            f"Session Time: {session_time//60}:{session_time%60:02d}",
            f"Photos Saved: {self.photos_saved}",
            f"Active Tracks: {len(self.object_tracker)}",
        ]

        for text in session_stats:
            cv2.putText(
                info_panel, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1
            )
            y_offset += line_height - 5

        # Controls
        cv2.putText(
            info_panel, "CONTROLS:", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )
        y_offset += line_height

        cv2.putText(
            info_panel, "  q=quit  s=save  r=reset  c=clear",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

        frame[10:10+panel_height, 10:10+panel_width] = info_panel


def get_youtube_stream_url(youtube_url: str) -> Optional[str]:
    """Extract direct stream URL from YouTube.

    Args:
        youtube_url (str): YouTube URL.

    Returns:
        Optional[str]: Direct stream URL or None if extraction fails.
    """
    try:
        import yt_dlp

        ydl_opts = {"format": "best[height<=720]/best", "quiet": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            logger.info("Extracted stream URL from YouTube")
            return info["url"]

    except ImportError:
        logger.error("yt-dlp not installed. Install with: pip install yt-dlp")
        return None
    except Exception as e:
        logger.error(f"Could not extract YouTube stream: {e}")
        return None


def setup_video_capture(video_url: Optional[str] = None) -> Optional[cv2.VideoCapture]:
    """Setup video capture from camera, URL, or YouTube.

    Args:
        video_url (Optional[str]): Video source URL or None for webcam.

    Returns:
        Optional[cv2.VideoCapture]: Opened video capture object or None.
    """
    if video_url:
        logger.info(f"Connecting to video: {video_url}")

        if "youtube.com" in video_url or "youtu.be" in video_url:
            logger.info("Detected YouTube URL, extracting stream...")
            stream_url = get_youtube_stream_url(video_url)
            if stream_url is None:
                logger.warning("Trying direct connection...")
                stream_url = video_url
        else:
            stream_url = video_url

        cap = cv2.VideoCapture(stream_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, BUFFER_SIZE)

        if not cap.isOpened():
            logger.error("Could not open video stream")
            return None

        ret, test_frame = cap.read()
        if not ret or test_frame is None:
            logger.error("Could not read from video stream")
            cap.release()
            return None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        logger.info(f"Video connected: {width}x{height} @ {fps} FPS")

    else:
        logger.info("Searching for local camera...")
        cap = None

        for camera_id in [0, 1, 2, 3]:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret and test_frame is not None:
                    logger.info(f"Camera {camera_id} connected")
                    break
                cap.release()
            else:
                logger.debug(f"Camera {camera_id} not available")

        if not cap or not cap.isOpened():
            logger.error("No camera found")
            return None

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, OPTIMAL_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, OPTIMAL_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, OPTIMAL_FPS)

    return cap


def main() -> None:
    """Main execution function."""
    logger.info("Enhanced Smart Traffic & People Counter")
    logger.info("Features: Vehicles, people counting, advanced tracking, photo capture")

    # Video source - change to None for webcam
    video_url = "https://www.youtube.com/watch?v=rnXIjl_Rzy4"

    counter = EnhancedTrafficPeopleCounter(video_url=video_url)
    cap = setup_video_capture(video_url)

    if cap is None:
        return

    logger.info("Starting counting system. Controls: q=quit, s=save, r=reset, c=clear")

    frame_count = 0
    fps_start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame")
                break

            frame_count += 1

            detected_objects = counter.detect_objects(frame)
            tracked_objects = counter.update_tracker(detected_objects)
            crossings = counter.check_line_crossings(tracked_objects, frame)
            counter.draw_enhanced_interface(frame, tracked_objects, crossings)

            # FPS calculation
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                fps = 30 / (fps_end_time - fps_start_time)
                counter.fps_history.append(fps)
                fps_start_time = fps_end_time

            if counter.fps_history:
                avg_fps = sum(counter.fps_history) / len(counter.fps_history)
                cv2.putText(
                    frame,
                    f"FPS: {avg_fps:.1f}",
                    (frame.shape[1] - 150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            cv2.imshow("Enhanced Traffic & People Counter", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"manual_save_{timestamp}.jpg"
                filepath = os.path.join(counter.save_directory, filename)
                cv2.imwrite(filepath, frame)
                logger.info(f"Manual save: {filename}")
            elif key == ord("r"):
                counter.car_count = 0
                counter.truck_count = 0
                counter.bus_count = 0
                counter.motorcycle_count = 0
                counter.people_count = 0
                counter.total_vehicles = 0
                counter.total_people = 0
                counter.photos_saved = 0
                counter.crossed_objects.clear()
                logger.info("All counters reset")
            elif key == ord("c"):
                counter.object_tracker.clear()
                counter.crossed_objects.clear()
                counter.object_id_counter = 0
                logger.info("Tracking history cleared")

    except KeyboardInterrupt:
        logger.info("Stopping counter")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        counter.save_statistics()

        logger.info("FINAL REPORT")
        logger.info(f"Vehicles: {counter.total_vehicles} "
                   f"(Cars: {counter.car_count}, Trucks: {counter.truck_count}, "
                   f"Buses: {counter.bus_count}, Other: {counter.motorcycle_count})")
        logger.info(f"People: {counter.total_people}")
        session_time = int(time.time() - counter.start_time)
        logger.info(f"Duration: {session_time//60}:{session_time%60:02d}")
        logger.info(f"Photos saved: {counter.photos_saved}")


if __name__ == "__main__":
    main()
