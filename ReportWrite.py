
# 
# NAME: SAMIP REGMI
# PROGRAM: FREQUENCY BASED AUDIO DETECTER
# JULY 5 2025 BASED ON MY ORIGINAL PROJECT
# COPYRIGHT SAMIP REGMI

# UPDATED ON JULY 10 , PLANS
# TO ADD THE LATEST IMAGE TO THE ONLINE API DB


# UPADTED ON JUL 15 
# SQL INTEGRATION
# 

# UPDATED ON JULY 16
#  EMAIL INTEGRATION



# JULY 19
# LOCAL IMAGE LOGS

import pandas as pd
import datetime
# import PIL.Image
import json
import csv
import os
import base64
import requests
import pandas as pd
import csv
import mysql.connector
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

# TODO: MAKE ALL THESE CRAP BETTER
# 1. RENAME TO ALL CONSTANTS
# ADD DOC STRINGS

github_id = 'samTime101'
github_repo = 'image_database'
github_folder = f'uploads'
image = './uploads/temp.png'
json_file_path = 'user.json'
sample_rate = 44100
duration = 2.0
tolerance = 0.0
space_name  = '2fa/records'
space_password = '2fa'
content = ''
timestamp = ''

with open(json_file_path, 'r') as f:
    users = json.load(f)

# users = [
#   { "name": "samipregmi", "frequency": 400, "secret": "np02cs4a240105" },
#   { "name": "srijanregmi", "frequency": 420, "secret": "np02cs4a240103" },
#   { "name": "nayannembang", "frequency": 440, "secret": "np02cs4a240109" }
# ]

# FREQUENCY INIT


attendance_date = datetime.date.today().isoformat()  

# TEST CODE
address = "https://samip.pythonanywhere.com"
def hello(name):
    print(f"Hello {name}!")

def write_data(name , timestamp = datetime.datetime.now().isoformat() ,today = datetime.date.today().isoformat() , attendence = "present"):
    '''
    write_data:
    write detected data in csv file
    '''
    # global timestamp
    print('....write _data ----')
    try:
        
        csv_file_path = '2fa.csv'

        already_marked = False
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if not row or len(row) < 3:
                        continue
                    if row[0] == today and row[1].lower() == name.lower() and row[2].lower() == attendence.lower():
                        already_marked = True
                        break

        if already_marked:
            print(f"attendance already marked for {name} on {today}")
            return 101

        
        file_exists = os.path.exists(csv_file_path)
        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # check if that user exist in users.json
            if name not in [user['name'] for user in users]:
                print(f"User {name} not found in users.json")
                return 102
            if not file_exists:
                writer.writerow(["date", "name", "attendance", "timestamp"])
            writer.writerow([today, name, attendence.lower(), timestamp])
            

        print(f"marked attendance for {name} on {today}")
        return 100
    except Exception as e:
        print("Error:", e)








def report(attendance_date=attendance_date):
    print('generating report')
    with open('user.json', 'r') as f:
        users_data = json.load(f)

    df = pd.read_csv('2fa.csv')


    all_users_list = [user['name'] for user in users_data]
    present_users = df[(df['date'] == attendance_date) & (df['attendance'] == 'present')]


    present_timestamps = present_users['timestamp'].tolist()

    present_users_list = present_users['name'].tolist()



    absent_users_list = list(set(all_users_list) - set(present_users_list))

    absent_timestamps = ['None' for _ in absent_users_list]

    attendance_count = {
        'Present': len(present_users_list),
        'Absent': len(absent_users_list)
    }

    # write None for timestamp of absent users

    with open(f'{attendance_date}.csv', 'w') as f:
        f.write("status,name,date,timestamp\n")
        for user in present_users_list:
            timestamp = present_timestamps[present_users_list.index(user)]
            f.write(f"present,{user},{attendance_date},{timestamp}\n")
        for user, timestamp in zip(absent_users_list, absent_timestamps):
            f.write(f"absent,{user},{attendance_date},{timestamp}\n")

    # save_data_remote()

# -----------------------------------------------------------------------------------------------------------


#  written on july 10 
def save_data_remote():
    headers = {"Content-Type": "application/json"}
    with open(f'{attendance_date}.csv', 'r') as f:
        content = f.read()
    print(content)
    url = f"{address}/write/{space_name}/{attendance_date}"
    json_data = {"password": space_password, "content": content}
    response = requests.post(url, headers=headers, json=json_data)

    try:
        if response.json().get('Error') == 'file already exists':
            url = f"{address}/edit/{space_name}/{attendance_date}"
            json_data = {"password": 'samip@admin', "new_content": content}
            response = requests.post(url, headers=headers, json=json_data)
            print("Edited:", response.text, response.status_code)
        else:
            print("Write response:", response.text, response.status_code)
    except ValueError:
        print("Non-JSON response:", response.text, response.status_code)



repo = f'{github_id}/{github_repo}'
return_link = ''
def save_to_github(person):
    path = f'{github_folder}/{attendance_date}_{person}.png'

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())  
    base64_string = encoded_string.decode('utf-8')
    url = f'https://api.github.com/repos/{repo}/contents/{path}'
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    body={
        "message" : f"{attendance_date}{person}",
        "content" : base64_string
    }   
    return_link = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    print(return_link)

    response = requests.put(url, headers=headers, json=body)



def save_to_remote_save_image(person):

    # df = pd.read_csv('2fa.csv')
    # timestamp = df[(df['date'] == attendance_date) & (df['name'] == person)]
    # timestamp_= timestamp['timestamp'].tolist()[0]
    path = f'{github_folder}/{attendance_date}_{person}.png'
    return_link = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    print(return_link)
    # convert timestamp to string

    print('on save_to_remote_save_image function')
    print(person)
    print(return_link)
    space_name_image = '2fa/images'
    image_name = f"{attendance_date}_{person}"
    headers = {"Content-Type": "application/json"}
    content = f'<img src="{return_link}">'       
    url = f"{address}/write/{space_name_image}/{image_name}"
    json_data = {"password": space_password, "content": content}
    response = requests.post(url, headers=headers, json=json_data)

    
def save_to_sql(att_date = attendance_date) :

    table_name = att_date.replace('-','_')
    conn = mysql.connector.connect(
    host="localhost",
    user="root",           
    password="",           
    database="2fa"     
)
    cursor = conn.cursor()
    
    #  Already table xa ki xaina
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = '2fa'
        AND table_name = %s
    """, (table_name,))
    table_exists = cursor.fetchone()[0] == 1

    # yedi xa vane delete garne , easier option to delete instead of updating via sql
    if table_exists:
        cursor.execute(f"DELETE FROM `{table_name}`;")

    # if table not exist , create garne manually (which we have to first time)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        status VARCHAR(20),
        name VARCHAR(50),
        date DATE,
        timestamp VARCHAR(100)
    )
""")

    # csv to pointer titles ko next line ma lagera savev garne
    with open(f'{att_date}.csv',newline= '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            cursor.execute(f"""
            insert into {table_name} values (%s, %s, %s, %s);

        """,row)
        conn.commit()
        conn.close()
        print('done')



def save_image_locally(person):
    folder_path = './image_logs'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    image_path = './uploads/temp.png'
    new_image_path = os.path.join(folder_path, f"{attendance_date}_{person}.png")
    
    with open(image_path, 'rb') as src_file:
        with open(new_image_path, 'wb') as dest_file:
            dest_file.write(src_file.read())
    
    print(f"Image saved locally at {new_image_path}")
    return new_image_path

# report()
# save_data_remote()
# save_to_sql('2025-07-15')
# save_image_locally('samipregmi')


# AUGUST 9 ,2025
# https://codemon.medium.com/how-to-generate-images-with-text-using-python-15c73fb96bf8
def write_image(username , date , timestamp ,server_message = "Attendence done\nUsing CLI SERVER\n",font_name="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",font_size=30)-> None:
    image_url  = f"{date}_{username}.png"
    folder_path = './image_logs'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    image_url = os.path.join(folder_path, image_url)
    print(f"image path: {image_url}")
    message = f"{server_message}{username}\n{timestamp}"
    WIDTH, HEIGHT = 640, 480
    image = Image.new("RGB", (WIDTH, HEIGHT), color="white")
    draw = ImageDraw.Draw(image)
    from PIL import ImageFont
    font = ImageFont.truetype(font_name, font_size)
    draw.text((10, 10), message, fill=(0, 0, 0) ,font=font)
    image.save(image_url)
