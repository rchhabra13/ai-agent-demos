# Object Detection: Vehicle and People Counter

Real-time object detection and tracking system using YOLOv8. Counts vehicles (cars, trucks, buses, motorcycles) and people crossing detection lines. Supports webcam, direct video URLs, and YouTube streams with advanced tracking and automatic photo capture.

## Features

- **Multi-Class Detection**: Cars, trucks, buses, motorcycles, bicycles, and people
- **Advanced Tracking**: Persistent object IDs with motion history
- **Multi-Line Detection**: Multiple horizontal detection lines for accuracy
- **Automatic Photo Capture**: Saves timestamped images of detections
- **Real-Time Statistics**: Live counting with session tracking
- **Stream Support**: Webcam, direct URLs, and YouTube videos
- **State Persistence**: Saves/loads statistics between sessions

## Quick Start

```bash
git clone https://github.com/rchhabra13/object_detection.git
cd object_detection
pip install -r requirements.txt

# For webcam:
python yt_detection.py

# For YouTube (edit video_url in main()):
python yt_detection.py
```

## Controls

| Key | Action |
|-----|--------|
| q | Quit application |
| s | Manual save current frame |
| r | Reset all counters |
| c | Clear tracking history |

## Configuration

| Parameter | Default | Notes |
|-----------|---------|-------|
| Model | YOLOv8n | Nano model for speed |
| Confidence | 0.3 | Lower = more detections |
| Max Distance | 100px | Tracking distance threshold |
| Save Directory | traffic_people_photos | Output folder for photos |

## Tech Stack

Python, OpenCV, YOLOv8, NumPy, yt-dlp

## License

MIT

**Credit**: Rishi Chhabra (rchhabra13)
