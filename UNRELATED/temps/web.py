from flask import Flask, request, jsonify, render_template
import os
from deepface import DeepFace
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_FOLDER = 'student_id'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def to_model(test_image_path, known_faces_folder=KNOWN_FACES_FOLDER):
    try:
        result = DeepFace.find(img_path=test_image_path, db_path=known_faces_folder, model_name="SFace")
        if len(result) > 0 and len(result[0]) > 0:
            identity_path = result[0].iloc[0]['identity']
            name = os.path.splitext(os.path.basename(identity_path))[0]
            return name
        return None
    except Exception as e:
        print(f"Error in face recognition: {e}")
        return None

@app.route('/')
def index():
    return render_template('web.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        name = to_model(filepath)
        
        os.remove(filepath)
        
        return jsonify({'name': name})
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True , port=5600)