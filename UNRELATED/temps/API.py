# JULY 7 
# changed to dynamic port writing

# COPYRIGHT SAMIP REGMI 2025


# JULY 22 , ADDED EMAIL FIELD

from flask import Flask, request, jsonify
import os
import json
import base64
from flask_cors import CORS
from subprocess import check_output



app = Flask(__name__)
CORS(app)

@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    secret_code = data.get('secret')
    email = data.get('email')
    photo = data.get('photo')

    if not username or not secret_code or not photo or not email:
        return jsonify({"error": "Missing required fields"}), 400
    
    json_file_path = 'user.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            users = json.load(f)
    else:
        users = []

    for user in users:
        if user['name'] == username or user['secret'] == secret_code:
            return jsonify({"error": "User already exists"}), 400

    student_id_folder = './student_id'
    if not os.path.exists(student_id_folder):
        os.makedirs(student_id_folder)
    
    photo_data = None
    try:
        photo_data = base64.b64decode(photo)
    except Exception as e:
        return jsonify({"error": f"Failed to decode image: {str(e)}"}), 400
    
    photo_path = os.path.join(student_id_folder, f"{username}.png")
    with open(photo_path, 'wb') as f:
        f.write(photo_data)

    new_user = {
        "name": username,
        "frequency": (users[-1]['frequency'] + 20) if users else 400,
        "secret": secret_code,
        "email":email
    }
    users.append(new_user)
    
    with open(json_file_path, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"message": "User created successfully"}), 201




if __name__ == '__main__':
    output = check_output(['hostname', '-I'])
    ipv4_address = output.decode().split()[0]
    port = 5000
    with open('API.txt', 'w') as f:
        f.write(f'http://{ipv4_address}:{port}')

    app.run(host='0.0.0.0', port=port, debug=False)
