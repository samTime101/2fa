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
import os
import csv
import time
import cv2
from scipy.signal import periodogram
# import PIL.Image
import json
import ReportWrite
from dotenv import load_dotenv
from deepface import DeepFace

load_dotenv()

genai.configure(api_key=os.getenv("AI_KEY"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

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




def to_model(test_image_path="person.png", known_faces_folder="student_id"):
    '''
    function: to_model
    returns : detected face name
    '''
    result = DeepFace.find(img_path=test_image_path, db_path=known_faces_folder, model_name="SFace" )
    
    if len(result) > 0 and len(result[0]) > 0:
        identity_path = result[0].iloc[0]['identity']
        name = os.path.splitext(os.path.basename(identity_path))[0]
        return name
    else:
        return None




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
            return to_model()
            







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
            print(f" Match found for {user_data['name']}!")
            write_data(user_data["name"])
            ReportWrite.save_data_remote()
            return True

    print("No match found — possibly spoofed or expired.")
    return False

def hello(name):
    print(f"Hello {name}!")

def write_data(name):
    '''
    write_data:
    write detected data in csv file
    '''
    try:
        today = datetime.date.today().isoformat()
        csv_file_path = '2fa.csv'

        already_marked = False
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row[0] == today and row[1].lower() == name.lower() and row[2].lower() == "present":
                        already_marked = True
                        break

        if already_marked:
            print(f"Attendance already marked for {name} on {today}")
            return

        timestamp = datetime.datetime.now().isoformat()
        file_exists = os.path.exists(csv_file_path)
        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["date", "name", "attendance", "timestamp"])
            writer.writerow([today, name, "present", timestamp])





        print(f"✅ Marked attendance for {name} on {today}")
    except Exception as e:
        print(" Error:", e)



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
        time.sleep(3)



def report():
    with open('user.json', 'r') as f:
        users_data = json.load(f)

    df = pd.read_csv('2fa.csv')
# date,name,attendance,timestamp
# 2025-07-05,samipregmi,present,2025-07-05T15:17:20.794959
    attendance_date = datetime.date.today().isoformat()  


    present_users = df[(df['date'] == attendance_date) & (df['attendance'] == 'present')]

    all_users_list = [user['name'] for user in users_data]


    timestamp_list = present_users['timestamp'].tolist()

    present_users_list = present_users['name'].tolist()
    print(present_users_list)
    print(all_users_list)



    absent_users_list = list(set(all_users_list) - set(present_users_list))

    print(f"Present Users on {attendance_date}: {present_users_list}")
    print(f"Absent Users on {attendance_date}: {absent_users_list}")

    attendance_count = {
        'Present': len(present_users_list),
        'Absent': len(absent_users_list)
    }


    with open(f'{attendance_date}.csv','w') as f:
        f.write("status,name,date\n") 
        for user in present_users_list:  
            f.write(f"present,{user},{attendance_date}\n")
        for user in absent_users_list:
            f.write(f"absent,{user},{attendance_date}\n")        
        



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
        report()
        exit(0)