from flask import Blueprint, request, jsonify, render_template
from deepface import DeepFace
from werkzeug.utils import secure_filename
import os
import pandas as pd
import base64
import json
import hashlib
from datetime import datetime
import threading
import ReportWrite

attendance_bp = Blueprint('attendance', __name__)

UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_FOLDER = 'student_id'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
tolerance = 0.0
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with open('./user.json') as f:
    users = json.load(f)

def generate_dynamic_frequency(user):
    now = datetime.utcnow().replace(second=0, microsecond=0)
    timestamp_str = now.isoformat() + 'Z'
    combo = f"{user['secret']}-{timestamp_str}"
    hash_hex = hashlib.sha256(combo.encode()).hexdigest()
    bias = int(hash_hex[-4:], 16) % 20
    return user['frequency'] + bias + now.minute

def save_base64_image(base64_string, filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return filepath

def to_model(test_image_path="./uploads/temp.png", known_faces_folder="student_id"):
    try:
        result = DeepFace.find(img_path=test_image_path, db_path=known_faces_folder, model_name="SFace")
        if len(result) > 0 and len(result[0]) > 0:
            identity_path = result[0].iloc[0]['identity']
            name = os.path.splitext(os.path.basename(identity_path))[0]
            return name
        else:
            return None
    except Exception as e:
        print(f"Error in face recognition: {e}")
        return None

@attendance_bp.after_app_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "img-src 'self' data:;"
    return response

@attendance_bp.route('/scan')
def index():
    return render_template('index.html')

@attendance_bp.route('/detect', methods=['POST'])
def detect():
    data = request.get_json()
    image_b64 = data.get("image")
    frequency = data.get("frequency")

    print("-------------------------------------")
    print("frequency:", frequency)

    print("dynamic frequency for all users:")
    for user in users:
        dynamic_freq = generate_dynamic_frequency(user)
        print(f"{user['name']}: {dynamic_freq}")

    if not image_b64 or frequency is None:
        return jsonify({"status": " Missing data", "name": ""}), 400

    filename = secure_filename("temp.png")
    image_path = save_base64_image(image_b64, filename)
    name_face = to_model()
    peak_freq = float(frequency)

    for user_data in users:
        expected_freq = generate_dynamic_frequency(user_data)
        if abs(peak_freq - expected_freq) <= tolerance and to_model() == user_data["name"]:
            print(f"Match found for {user_data['name']}!")
            if ReportWrite.write_data(user_data['name']) == 100:
                print(f"Attendance marked for {user_data['name']}")
                ReportWrite.report()
                threading.Thread(target=ReportWrite.save_image_locally, args=(user_data['name'],)).start()
                return jsonify({"status": "Attendance marked", "name": user_data['name']}), 200
            else:
                print(f"Attendance already marked for {user_data['name']}")
                ReportWrite.report()
                threading.Thread(target=ReportWrite.save_image_locally, args=(user_data['name'],)).start()
                return jsonify({"status": "DONE Attendance already marked", "name": user_data['name']}), 200

    print("No match found — possibly spoofed or expired.")
    return jsonify({"status": "No match found", "name": ""}), 400

@attendance_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200
