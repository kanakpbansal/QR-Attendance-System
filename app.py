from flask import Flask, render_template, request, jsonify
import cv2
import sqlite3
import geocoder
from datetime import datetime

app = Flask(__name__)

def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    while True:
        ret, img = cap.read()
        if not ret:
            continue
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return data
        cv2.imshow("QR Scanner", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    return None

def get_location():
    g = geocoder.ip("me")
    return g.latlng if g.latlng else (0.0, 0.0)

def mark_attendance(qr_data):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, qr_data TEXT, location TEXT, timestamp TEXT)")
    location = str(get_location())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO attendance (qr_data, location, timestamp) VALUES (?, ?, ?)", (qr_data, location, timestamp))
    conn.commit()
    conn.close()

def get_attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    records = c.fetchall()
    conn.close()
    return records

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    qr_data = scan_qr()
    if qr_data:
        mark_attendance(qr_data)
        return jsonify({"status": "success", "message": "Attendance marked!"})
    return jsonify({"status": "error", "message": "No QR code detected."})

@app.route("/attendance")
def attendance():
    records = get_attendance()
    return jsonify(records)

if __name__ == "__main__":
    app.run(debug=True)