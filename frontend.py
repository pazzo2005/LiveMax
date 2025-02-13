import streamlit as st
import requests
import cv2
import tempfile
import os

st.title("🔆 Smart Infrastructure Dashboard")

# Upload video file
uploaded_file = st.file_uploader("Upload a video for occupancy detection", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Save video to a temporary file
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Display video
    st.video(video_path)

    st.success("📡 Video uploaded successfully! AI will now process the video.")

    # Send video path to AI detection script (Update ai_detection.py to accept this)
    requests.post("http://127.0.0.1:5000/upload", json={"video_path": video_path})

# Fetch power logs
response = requests.get("http://127.0.0.1:5000/logs")
logs = response.json()

# Show room status
if logs and logs[0][1] == "Occupied":
    st.success("🟢 Room is Occupied - Power ON")
else:
    st.warning("🔴 Room is Empty - Power OFF")

st.subheader("📊 Power Usage Logs")
st.table(logs)
