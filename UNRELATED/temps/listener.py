# 
# NAME: SAMIP REGMI
# PROGRAM: FREQUENCY BASED AUDIO DETECTER
# JULY 5 2025 BASED ON MY ORIGINAL PROJECT
# COPYRIGHT SAMIP REGMI
# 


import numpy as np
import sounddevice as sd
import google.generativeai as genai
import matplotlib.pyplot as plt
import pandas as pd
import hashlib
import datetime
import cv2
from scipy.signal import periodogram
# import PIL.Image
import json

json_file_path = 'user.json'

with open(json_file_path, 'r') as f:
    users = json.load(f)

# users = [
#   { "name": "samipregmi", "frequency": 400, "secret": "np02cs4a240105" },
#   { "name": "srijanregmi", "frequency": 420, "secret": "np02cs4a240103" },
#   { "name": "nayannembang", "frequency": 440, "secret": "np02cs4a240109" }
# ]

# FREQUENCY INIT
sample_rate = 44100
duration = 2.0
tolerance = 0.0



# R_DATA WITH GEMINI MODEL

# def r_data(i_name):
#     '''
#     function : r_data
#     parameters: i_name
#     returns name
#     '''
#     print(f"from function {i_name}")
#     with open('ocrPROMPT.txt','r') as ocrPROMPT:
#         prompt_final = ocrPROMPT.read()

#     ret_image = PIL.Image.open(i_name)

#     response_new = model.generate_content([ret_image,prompt_final])
#     for line in response_new.text.splitlines():
#         if line.startswith("name:"):
#             name = line.split(":")[1].strip().replace(" ", "").lower()
#             print(name)
#             return name



# GEMINI KO MODELLLL
# def to_model():
#     with open('comparePROMPT.txt','r') as comparePROMPT:
#         prompt = comparePROMPT.read()

#     student_id_folder = './student_id'
#     person_image_path = './person.png'

#     sample_file_2 = PIL.Image.open(person_image_path)

#     matches = {}
#     for file_name in os.listdir(student_id_folder):
#         if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
#             database = os.path.join(student_id_folder, file_name)
#             print(f"Using {file_name} for comparison...")
#             sample_file_1 = PIL.Image.open(database)
            
#             response = model.generate_content([prompt, sample_file_1, sample_file_2])
#             response_data = response.text.strip().splitlines()
        
#             return_data = int(response_data[1])
#             confidence = float((response_data[3]))

#             print(f"Returned :{return_data}")
#             print(f"Conficence: {confidence}")

#             sample_file_1 = PIL.Image.open(database)
#             if return_data == 1:
#                 print(f'Potential match with confidence {confidence}')
#                 matches[database] = confidence
#                 print(matches)
#                 continue
#     max_conf = 0.0
#     max_loc = None
#     for image,conf in matches.items():
#         if conf>max_conf:
#             max_conf = conf
#             max_loc = image


#     if max_loc:
#         with open('match.tx        # if time.time() - time_started > 10:
        #     print("Time limit exceeded, generating report...")
        #     breakt','w') as match:
#             match.write(max_loc)
#         return r_data(max_loc)
#     else:
#         print("❌ No match found with return_data == 1. Skipping write and r_data() call.")








def cam():
    '''
    function: cam
    init camera , capturing image
    '''
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            img_name = f"person.png"
            cv2.imwrite(img_name, frame)
            print(f"{img_name} written!")
            







def generate_dynamic_frequency(user_data):

    '''
    final_frequency = base_frequency + bias(added with hash value ) + minute(changes every minute)
    
    '''
    base_freq = user_data["frequency"]
    secret_key = user_data["secret"]

    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    time_hz = now.minute
    timestamp_str = now.replace(tzinfo=None).isoformat() + 'Z'

    # now = datetime.datetime.utcnow()
    # time_hz = now.minute
    # timestamp_str = now.strftime("%Y-%m-%dT%H:%M:00.000Z") 

    print(timestamp_str)

    combo = f"{secret_key}-{timestamp_str}"
    hash_digest = hashlib.sha256(combo.encode()).hexdigest()
    hash_val = int(hash_digest[-4:], 16)
    bias = hash_val % 20

    final_frequency = base_freq + bias + time_hz

    # print(f"[{users['name'][user_index]}] Base: {base_freq} Hz, Bias: {bias} Hz, Minute: {time_hz}, Final: {final_frequency:.2f} Hz")
    return final_frequency


def detect_frequency():
    '''
    detect_frequency
    detects frequency for every data
    '''
    print("🎤 Listening for frequency...")

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()
    
    frequencies, power = periodogram(audio.flatten(), sample_rate)
    peak_freq = frequencies[np.argmax(power)]


    return peak_freq

def verify_frequency(peak_freq):
    '''
    verify frequency:
    checks and verifies frequency
    '''
    for user_data in users:
        expected_freq = generate_dynamic_frequency(user_data)
        # print(f"Expected frequency for {user_data['name']}: {expected_freq:.2f} Hz")
        
        if abs(peak_freq - expected_freq) <= tolerance:
            print(f"Detected : {user_data['name']}")
        if abs(peak_freq - expected_freq) <= tolerance and cam() == user_data["name"]:
            print(f"✅ Match found for {user_data['name']}!")
            return True

    print("❌ No match found — possibly spoofed or expired.")
    return False





def main():
    '''
    main():
    program entry point
    '''
    # time_started = time.time()
    while True:
        detected_freq = detect_frequency()
        if verify_frequency(detected_freq):
            print("Attendance marked successfully!")
            cv2.destroyAllWindows()

        else:
            print("No valid attendance found.")
            cv2.destroyAllWindows()
        print("Waiting for the next frequency input...\n")
        # if time.time() - time_started > 10:
        #     print("Time limit exceeded, generating report...")
        #     break
        # time.sleep(3)






if __name__ == "__main__":

    try:
        # time_started = time.time()
        # print(f"Program started at {time_started}")
        main()
        # if time.time() - time_started > 10:
        #     print("Time limit exceeded, generating report...")
        #     report()
        #     exit(0)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Generating report...")
        exit(0)