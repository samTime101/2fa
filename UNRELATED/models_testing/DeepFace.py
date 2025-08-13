from deepface import DeepFace
import os

def to_model(test_image_path="person.png", known_faces_folder="student_id"):
    result = DeepFace.find(img_path=test_image_path, db_path=known_faces_folder, model_name="SFace")
    
    if len(result) > 0 and len(result[0]) > 0:
        identity_path = result[0].iloc[0]['identity']
        name = os.path.splitext(os.path.basename(identity_path))[0]
        return name
    else:
        return None