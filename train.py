# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

# import tensorflow as tf
# tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
# tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())

# from deepface import DeepFace
# from sklearn.preprocessing import LabelEncoder
# from sklearn.svm import SVC
# import pickle
# import time

# dataset_path = "student_id"
# embeddings = []
# labels = []

# image_files = [f for f in os.listdir(dataset_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
# total_images = len(image_files)
# print(f"Found {total_images} images for training.\n")

# start_time = time.time()

# for idx, img_name in enumerate(image_files, start=1):
#     img_path = os.path.join(dataset_path, img_name)
#     label = os.path.splitext(img_name)[0]
#     try:
#         embedding = DeepFace.represent(img_path=img_path, model_name='Facenet')[0]["embedding"]
#         embeddings.append(embedding)
#         labels.append(label)
#         elapsed = time.time() - start_time
#         print(f"[{idx}/{total_images}] TRAINED: {img_name} | Time elapsed: {elapsed:.1f}s")
#     except Exception as e:
#         print(f"[{idx}/{total_images}] Skipping {img_name}: {e}")

# print("\nEncoding labels...")
# le = LabelEncoder()
# labels_encoded = le.fit_transform(labels)

# print("Training SVM classifier...")
# clf = SVC(kernel='linear', probability=True)
# clf.fit(embeddings, labels_encoded)

# with open("deepface_svm.pkl", "wb") as f:
#     pickle.dump(clf, f)
# with open("label_encoder.pkl", "wb") as f:
#     pickle.dump(le, f)

# print(f"Training complete in {time.time() - start_time:.1f} sec_onds.")
import os
import pickle
import time
from deepface import DeepFace
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import tensorflow as tf

# -------------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   
tf.config.threading.set_intra_op_parallelism_threads(os.cpu_count())
tf.config.threading.set_inter_op_parallelism_threads(os.cpu_count())

# -------------------------------
dataset_path = "student_id"
cache_file = "embeddings_cache.pkl"
embeddings = []
labels = []
cache = {}

if os.path.exists(cache_file):
    with open(cache_file, "rb") as f:
        cache = pickle.load(f)
    print(f"Loaded cache with {len(cache)} entries.")

# -------------------------------
image_files = [f for f in os.listdir(dataset_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
total_images = len(image_files)
print(f"Found {total_images} images for training.\n")

start_time = time.time()
updated_cache = cache.copy()

for idx, img_name in enumerate(image_files, start=1):
    img_path = os.path.join(dataset_path, img_name)
    label = os.path.splitext(img_name)[0]
    file_stat = os.stat(img_path)
    file_info = (file_stat.st_size, file_stat.st_mtime)

    if img_name in cache and cache[img_name]["info"] == file_info:
        embedding = cache[img_name]["embedding"]
        print(f"[{idx}/{total_images}] Cached: {img_name}")
    else:
        embedding = DeepFace.represent(img_path=img_path, model_name='Facenet')[0]["embedding"]
        updated_cache[img_name] = {"embedding": embedding, "info": file_info}
        print(f"[{idx}/{total_images}] Processed: {img_name}")

    embeddings.append(embedding)
    labels.append(label)

with open(cache_file, "wb") as f:
    pickle.dump(updated_cache, f)

# -------------------------------
print("\nEncoding labels...")
le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

print("Training SVM classifier...")
clf = SVC(kernel='linear', probability=True)
clf.fit(embeddings, labels_encoded)

with open("deepface_svm.pkl", "wb") as f:
    pickle.dump(clf, f)
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print(f"Training complete in {time.time() - start_time:.1f} seconds.")
print("Model, label encoder, and cache saved successfully!")
