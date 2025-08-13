import os
import cv2
import time
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

def to_model(test_image_path="person.png", known_faces_folder="student_id"):
    

    model = FaceAnalysis(name='buffalo_l')  
    model.prepare(ctx_id=0)

    known_embeddings = []
    known_names = []

    for filename in os.listdir(known_faces_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(known_faces_folder, filename)
        img = cv2.imread(img_path)
        faces = model.get(img)

        if faces:
            known_embeddings.append(faces[0].embedding)
            known_names.append(os.path.splitext(filename)[0])
        else:
            print(f"No face found in {filename}")

    test_img = cv2.imread(test_image_path)
    test_faces = model.get(test_img)

    if not test_faces:
        print(" No face found in test image.")
        return None

    test_embedding = test_faces[0].embedding

    similarities = cosine_similarity([test_embedding], known_embeddings)[0]
    best_match_index = np.argmax(similarities)
    confidence = similarities[best_match_index]


    if confidence > 0.6: 
        matched_name = known_names[best_match_index]
        print(f"Matched with: {matched_name} (confidence: {confidence:.3f})")
    else:
        matched_name = None
        print("No match found")

    return matched_name

to_model()