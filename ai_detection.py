import cv2
import torch
import paho.mqtt.client as mqtt
import requests
import time

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# MQTT Setup
MQTT_BROKER = "mqtt.eclipseprojects.io"
MQTT_TOPIC = "room/occupancy"

client = mqtt.Client()
try:
    client.connect(MQTT_BROKER, 1883, 60)
    print("✅ Connected to MQTT broker")
except Exception as e:
    print(f"❌ MQTT Connection Failed: {e}")

def fetch_video_path():
    """Fetch video path from API, fallback if it fails."""
    try:
        response = requests.get("http://127.0.0.1:5000/get_video")
        video_path = response.json().get("video_path", "sample_video.mp4")
        print(f"📹 Using video: {video_path}")
        return video_path
    except Exception as e:
        print(f"❌ API Error: {e}, using default video.")
        return "sample_video.mp4"

def detect_occupancy():
    """Detect people using YOLOv5 and send MQTT updates."""
    video_path = fetch_video_path()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("⚠️ End of video. Restarting...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
            continue

        results = model(frame)  # Run YOLOv5 on frame

        # Extract bounding boxes and class labels
        detections = results.xyxy[0].cpu().numpy()
        people_count = sum(1 for obj in detections if int(obj[5]) == 0)  # Class 0 = Person
        
        print(f"👥 People Detected: {people_count}")

        if people_count > 0:
            client.publish(MQTT_TOPIC, "Occupied")
            print("🟢 Room is Occupied")
            requests.post("http://127.0.0.1:5000/log", json={"status": "Occupied"})
        else:
            client.publish(MQTT_TOPIC, "Empty")
            print("🔴 Room is Empty - Turning off devices.")
            requests.post("http://127.0.0.1:5000/log", json={"status": "Empty"})

        # Display video feed with detections
        results.render()
        cv2.imshow("Occupancy Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()
    print("✅ Disconnected from MQTT broker.")

if __name__ == "__main__":
    detect_occupancy()
