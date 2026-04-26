from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
import webbrowser
import csv
import os

app = Flask(__name__)
CORS(app)

# Paths
model_path = r"C:\Users\santhosh\OneDrive\Desktop\analysisoftraffic\runs\detect\yolov8s-cam8-finetune3\weights\best.pt"
roi_path = r"C:\Users\santhosh\OneDrive\Desktop\analysisoftraffic\smart_traffic_analytics_dashboard\smart_traffic_analytics_dashboard\roi.npy"
video_path = r"C:\Users\santhosh\OneDrive\Desktop\analysisoftraffic\smart_traffic_analytics_dashboard\smart_traffic_analytics_dashboard\test_video.mp4"
csv_file_path = r"C:\Users\santhosh\OneDrive\Desktop\analysisoftraffic\smart_traffic_analytics_dashboard\smart_traffic_analytics_dashboard\traffic_stats.csv"

# Load model and ROI
model = YOLO(model_path)
roi_polygon = np.load(roi_path).tolist()

# Class and color maps
VEHICLE_CLASSES = {
    0: 'car', 1: 'motorbike', 2: 'bicycle', 3: 'person', 4: 'truck',
    5: 'minitruck', 6: 'van', 7: 'taxi', 8: 'MTC', 9: 'privatebus',
    10: 'auto', 11: 'ambulance'
}
BOX_COLORS = {
    'car': (180, 119, 31),
    'motorbike': (14, 127, 255),
    'bicycle': (44, 160, 44),
    'truck': (40, 39, 214),
    'minitruck': (189, 103, 148),
    'van': (75, 86, 140),
    'taxi': (194, 119, 227),
    'MTC': (127, 127, 127),
    'privatebus': (34, 189, 188),
    'auto': (207, 190, 23),
    'ambulance': (147, 20, 255),
    'person': (0, 255, 255)
}

# Global shared states
frame_data = []
current_frame = None
lock = threading.Lock()
latest_stats = []
seen_ids_per_class = {v: set() for v in VEHICLE_CLASSES.values()}


def is_inside_polygon(point, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, False) >= 0


def generate_frames():
    global current_frame, frame_data, latest_stats, seen_ids_per_class

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_number, last_processed_second = 0, -1

    frame_data.clear()
    latest_stats.clear()
    seen_ids_per_class = {v: set() for v in VEHICLE_CLASSES.values()}

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        headers = ["second"] + list(VEHICLE_CLASSES.values()) + ["cumulative_total", "cumulative_vehicle_only"] + [f"cumulative_{v}" for v in VEHICLE_CLASSES.values()]
        writer.writerow(headers)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame_number += 1
        counts = {v: 0 for v in VEHICLE_CLASSES.values()}
        cv2.polylines(frame, [np.array(roi_polygon, dtype=np.int32)], True, (0, 255, 255), 2)

        results = model.track(frame, persist=True, tracker="bytetrack.yaml")[0]
        if results.boxes.id is not None:
            ids = results.boxes.id.cpu().numpy()
            boxes = results.boxes.xyxy.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy()

            for track_id, box, cls_id in zip(ids, boxes, class_ids):
                cls_id = int(cls_id)
                if cls_id not in VEHICLE_CLASSES:
                    continue
                name = VEHICLE_CLASSES[cls_id]
                x1, y1, x2, y2 = map(int, box)
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                if is_inside_polygon(center, roi_polygon):
                    counts[name] += 1
                    seen_ids_per_class[name].add(int(track_id))
                    color = BOX_COLORS[name]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        second = int(frame_number // fps)
        if second != last_processed_second:
            last_processed_second = second
            cumulative_total = sum(len(v) for v in seen_ids_per_class.values())
            cumulative_vehicle_only = sum(len(seen_ids_per_class[k]) for k in seen_ids_per_class if k != "person")

            stats = {
                "frame": frame_number,
                "second": second,
                "counts": counts,
                "total": sum(counts.values()),
                "cumulative_counts": {k: len(v) for k, v in seen_ids_per_class.items()},
                "cumulative_total": cumulative_total,
                "cumulative_vehicle_only": cumulative_vehicle_only
            }

            with lock:
                frame_data.append(stats)
                latest_stats = frame_data[-60:]

            row = [second] + [counts[v] for v in VEHICLE_CLASSES.values()] + \
                  [cumulative_total, cumulative_vehicle_only] + [len(seen_ids_per_class[v]) for v in VEHICLE_CLASSES.values()]

            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

        # ✅ Updated: Always update frame without skipping
        with lock:
            current_frame = frame.copy()

    cap.release()


@app.route("/")
def index():
    return "<h2>Flask Backend Running</h2>"


@app.route("/video_feed")
def video_feed():
    def generate():
        while True:
            with lock:
                if current_frame is None:
                    continue
                _, buffer = cv2.imencode('.jpg', current_frame)
                frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/stats")
def stats():
    with lock:
        return jsonify(latest_stats)


if __name__ == "__main__":
    threading.Thread(target=generate_frames, daemon=True).start()
    threading.Thread(target=lambda: webbrowser.open("http://localhost:4028"), daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)
