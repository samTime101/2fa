import face_recognition
import os
import cv2
import time

def to_model(test_image_path="person.png", known_faces_folder="student_id", resize_scale=0.5):
    start_time = time.time() 

    known_encodings = []
    known_names = []

    # Load and encode known faces
    for filename in os.listdir(known_faces_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        image_path = os.path.join(known_faces_folder, filename)
        image = face_recognition.load_image_file(image_path)
        image_small = cv2.resize(image, (0, 0), fx=resize_scale, fy=resize_scale)

        encodings = face_recognition.face_encodings(image_small)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
        else:
            print(f"[!] No face found in {filename}")

    # Load and encode test image
    test_image = face_recognition.load_image_file(test_image_path)
    test_image_small = cv2.resize(test_image, (0, 0), fx=resize_scale, fy=resize_scale)
    test_encodings = face_recognition.face_encodings(test_image_small)

    if not test_encodings:
        print("[!] No face found in test image.")
        return None

    test_encoding = test_encodings[0]
    results = face_recognition.compare_faces(known_encodings, test_encoding)
    distances = face_recognition.face_distance(known_encodings, test_encoding)

    best_match_index = distances.argmin()
    end_time = time.time()  # ⏱ End timing
    elapsed = end_time - start_time

    if results[best_match_index]:
        print(f"Matched with: {known_names[best_match_index]}")
    else:
        print("No match found")

    print(f"[⏱️] Time taken: {elapsed:.3f} seconds")
    return known_names[best_match_index] if results[best_match_index] else None

to_model()
