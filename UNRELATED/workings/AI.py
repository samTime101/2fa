import cv2
import PIL.Image
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import datetime
import csv

load_dotenv()

genai.configure(api_key=os.getenv("AI_KEY"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")




def write_data():
    try:
        with open('data.txt', 'r') as responsex:
            response = responsex.read()
            response_data = response.strip().splitlines()
            name = response_data[0].split(":")[1].strip()

        today = datetime.date.today().isoformat() 
        csv_file_path = 'attendance.csv'

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
            print(f"✅ Attendance already marked for {name} on {today}")
            return

        timestamp = datetime.datetime.now().isoformat()

        file_exists = os.path.exists(csv_file_path)
        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["date", "name", "attendence", "timestamp"]) 
            writer.writerow([today, name, "present", timestamp])

        print(f"✅ Marked attendance for {name} on {today}")

    except Exception as e:
        print("❌ Error:", e)






def r_data(i_name):
    print(f"from function {i_name}")
    with open('ocrPROMPT.txt','r') as ocrPROMPT:
        prompt_final = ocrPROMPT.read()

    ret_image = PIL.Image.open(i_name)

    response_new = model.generate_content([ret_image,prompt_final])
    f = open("data.txt", "w")
    f.write(response_new.text)
    f.close()
    write_data()

def to_model():
    with open('comparePROMPT.txt','r') as comparePROMPT:
        prompt = comparePROMPT.read()

    student_id_folder = './student_id'
    person_image_path = './person.png'

    sample_file_2 = PIL.Image.open(person_image_path)

    matches = {}
    for file_name in os.listdir(student_id_folder):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            database = os.path.join(student_id_folder, file_name)
            print(f"Using {file_name} for comparison...")
            sample_file_1 = PIL.Image.open(database)
            
            response = model.generate_content([prompt, sample_file_1, sample_file_2])
            response_data = response.text.strip().splitlines()
        
            return_data = int(response_data[1])
            confidence = float((response_data[3]))

            print(f"Returned :{return_data}")
            print(f"Conficence: {confidence}")

            sample_file_1 = PIL.Image.open(database)
            if return_data == 1:
                print(f'Potential match with confidence {confidence}')
                matches[database] = confidence
                print(matches)
                continue
    max_conf = 0.0
    max_loc = None
    for image,conf in matches.items():
        if conf>max_conf:
            max_conf = conf
            max_loc = image


    if max_loc:
        with open('match.txt','w') as match:
            match.write(max_loc)
        r_data(max_loc)
    else:
        print("❌ No match found with return_data == 1. Skipping write and r_data() call.")





def cam():
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
            to_model()
            

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    cam()
    # write_data()
    # to_model()