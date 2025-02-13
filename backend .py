from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Initialize database
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS power_usage (id INTEGER PRIMARY KEY, status TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
conn.commit()

# Store video path globally
video_path = "sample_video.mp4"  # Default video

@app.route("/upload", methods=["POST"])
def upload_video():
    global video_path
    data = request.json
    video_path = data["video_path"]
    return jsonify({"message": "Video path updated"}), 200

@app.route("/get_video", methods=["GET"])
def get_video():
    return jsonify({"video_path": video_path})

@app.route("/log", methods=["POST"])
def log_power_usage():
    data = request.json
    status = data["status"]
    cursor.execute("INSERT INTO power_usage (status) VALUES (?)", (status,))
    conn.commit()
    return jsonify({"message": "Logged Successfully"}), 201

@app.route("/logs", methods=["GET"])
def get_logs():
    cursor.execute("SELECT * FROM power_usage ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)
