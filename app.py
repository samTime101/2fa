# SAMIP REGMI 2025
#  JULY 5 , REMOVING GEMINI FACE RECOG WITH DEEP FACE
# JULY 15 IMAGE LOGGING
# SQL INTEGRATION


# SAMIP REGMI
# JULY 17 GRAPHHHHHHH


import pickle
from flask import Flask, request, jsonify, render_template
from deepface import DeepFace
from werkzeug.utils import secure_filename
import os
import pandas as pd
import base64
import json
import hashlib
from datetime import datetime , date
import csv
import time
import ReportWrite
from flask_cors import CORS
import threading
import google.generativeai as genai
from flask_mail import Mail, Message
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
CORS(app)

# IMAGE PREVIEW BLOCK NA HOS
# https://stackoverflow.com/questions/40360109/content-security-policy-img-src-self-data





@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "img-src 'self' data:;"
    return response


# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# mail = Mail(app)

# def send_attendance_email(to_email, name):
#     try:
#         msg = Message(
#             subject="Attendance Marked",
#             recipients=[to_email],
#             body=f"Hi {name}, your attendance was successfully marked at {datetime.now().strftime('%H:%M:%S on %Y-%m-%d')}."
#         )
#         mail.send(msg)
#         print(f"Email sent to {to_email}")
#     except Exception as e:
#         print(f"Email sending failed: {e}")

UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_FOLDER = 'student_id'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
tolerance = 0.0
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# genai.configure(api_key='AIzaSyDFCIayZbhDN-mpkw5SGshjrMpIYm9b6NU')
# model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

    

# def to_model(prompt):
#     with open('2fa.csv', 'r') as file:
#         content = file.read()
#     with open('user.json', 'r') as file:
#         users = file.read()

#     instruction = (
#         "Do not use any markdown formatting like **bold**, *italic*, `code`, or tables. "
#         "Respond only using plain text. Use line breaks and spacing for clarity."
#     )

#     full_prompt = instruction + "\n\n" + prompt
#     response = model.generate_content([full_prompt, content, users])
#     return response.text.strip()


# @app.route('/analysis', methods=['POST'])
# def get_response():
#     data = request.get_json()
#     prompt = data.get("prompt", "").strip()
#     if not prompt:
#         return jsonify({"response": "No prompt provided."})
    
#     answer = to_model(prompt)
#     return jsonify({"response": answer})


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

# def to_model(image_path):
#     try:
#         result = DeepFace.find(img_path=image_path, db_path=KNOWN_FACES_FOLDER, model_name="SFace")
#         if len(result) > 0 and len(result[0]) > 0:
#             identity_path = result[0].iloc[0]['identity']
#             name = os.path.splitext(os.path.basename(identity_path))[0]
#             return name
#     except Exception as e:
#         print("Face recognition error:", e)
#     return None


# def to_model(test_image_path="./uploads/temp.png", known_faces_folder="student_id"):
#     '''
#     function: to_model
#     returns : detected face name
#     '''
#     try:
#         print('----------using----------------')
#         known_faces = os.listdir(known_faces_folder)
#         print(f"Known faces in folder '{known_faces_folder}': {known_faces}")
#         result = DeepFace.find(img_path=test_image_path, db_path=known_faces_folder, model_name="SFace")
#         print(f'\n--------------{result}---------------\n')
#         if len(result) > 0 and len(result[0]) > 0:
#             identity_path = result[0].iloc[0]['identity']
#             name = os.path.splitext(os.path.basename(identity_path))[0]
#             return name
#         else:
#             return None
#     except Exception as e:
#         print(f"Error in face recognition: {e}")
#         return None



def to_model(test_image_path = "uploads/temp.png"):
    print('-----------------USING MODEL-----------------')
    clf = pickle.load(open("deepface_svm.pkl", "rb"))
    le = pickle.load(open("label_encoder.pkl", "rb"))
    try:
        embedding = DeepFace.represent(img_path=test_image_path, model_name='Facenet')[0]["embedding"]
        
        pred = clf.predict([embedding])
        name = le.inverse_transform(pred)[0]
        print(f"MODEL RECOGNIZED: {name}")
        return name
    except Exception as e:
        print(f"Error in recognition: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": "No JSON received"}), 400

    image_b64 = data.get("image")
    frequency = data.get("frequency")

    if not image_b64 or frequency is None:
        return jsonify({"status": "Missing data", "name": ""}), 400

    try:
        peak_freq = float(frequency)
    except ValueError:
        return jsonify({"status": "Invalid frequency", "name": ""}), 400

    photo_path = os.path.join(UPLOAD_FOLDER, "temp.png")
    with open(photo_path, "wb") as f:
        f.write(base64.b64decode(image_b64))

    print("Running face recognition...")
    for user_data in users:
        expected_freq = generate_dynamic_frequency(user_data)
        print(f"expected_freq: {expected_freq}, peak_freq: {peak_freq}, tolerance: {tolerance}")
        if abs(peak_freq - expected_freq) <= tolerance and to_model(photo_path) == user_data['name']:
            print(f"Match found for {user_data['name']}!")

            if ReportWrite.write_data(user_data['name']) == 100:
                print(f"Attendance marked for {user_data['name']}")
                ReportWrite.report()
                threading.Thread(target=ReportWrite.save_image_locally, args=(user_data['name'],)).start()
                threading.Thread(target=ReportWrite.save_to_sql).start()
                return jsonify({"status": "Attendance marked", "name": user_data['name']}), 200
            else:
                print(f"Attendance already marked for {user_data['name']}")
                ReportWrite.report()
                threading.Thread(target=ReportWrite.save_to_sql).start()
                return jsonify({"status": "Attendance already marked", "name": user_data['name']}), 200

    print("No match found — possibly spoofed or expired.")
    return jsonify({"status": "No match found", "name": ""}), 400




@app.route('/users', methods=['GET'])
def get_users():
    with open('./user.json') as f:
        users = json.load(f)
    return jsonify(users), 200
        

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.get_json()
    if not data or 'photo' not in data:
        return jsonify({'error': 'No photo provided'}), 400

    photo_base64 = data['photo']
    photo_path = os.path.join(UPLOAD_FOLDER, "temp.png")

    try:
        with open(photo_path, "wb") as f:
            f.write(base64.b64decode(photo_base64))
        
        name = to_model(photo_path)

        return jsonify({'name': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/user_model_test', methods=['GET'])
def user_model_test():
    return render_template('user_model_test.html')
if __name__ == '__main__':
    app.run(debug=True , port = 5500 , host="0.0.0.0")
