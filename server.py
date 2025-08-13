# NO NEW LINE , ONLY FOR LINUX AND POSIX COMPATIBILITY

# --------------------------------------------------------------
# CREDITS TO https://github.com/TiagoValdrich/python-socket-chat

# JULY 17 CHANGED BY SAMIP REGMI samTime101

# TODO: JULY 17

# connection.send(b"")
# connection.recv(somebytes).decode().strip

# check credentials 
# if not ok
# conn..send('invalid')
# remove_connection(conn)

# else
# succkess
# go to while loop

# JULY 20 , AI INTEGRATION

import socket, threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ReportWrite
import json
import pyotp
import time
# import hashlib
from datetime import datetime,date
from dotenv import load_dotenv
import os
import google.generativeai as genai

# from analysis import to_model
import pandas as pd
# import datetime
import os

connections = []
load_dotenv()
genai.configure(api_key=os.getenv('USING_GEMINI_KEY'))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")




today_date = date.today().isoformat()  


MAIL_USERNAME= os.getenv('MAIL_USERNAME')
MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER= os.getenv('MAIL_SERVER')

print(MAIL_USERNAME)
print(MAIL_PASSWORD)
print(MAIL_DEFAULT_SENDER)

JSON_FILE_PATH = 'user.json'

def read_json()->str:
    with open(JSON_FILE_PATH, 'r') as f:
        users = json.load(f)
        return users

today = date.today().isoformat()


def to_model(prompt):
    with open('2fa.csv', 'r') as file:
        content = file.read()
    with open('user.json', 'r') as file:
        users = file.read()

    instruction = (
        f"today is {today} and the data is from 2fa.csv and user.json, "
        "Do not use any markdown formatting like **bold**, *italic*, `code`, or tables. "
        "Respond only using plain text. Use line breaks and spacing for clarity."
        "IF THE PERSON ASKED BY USER IS NOT ON BOTH THE FILES THEN ANSWER 'PERSON NOT FOUND IN RECORDS'."
        "DONT ANSWER SECRET CODE OR BASE FREQUENCY OF USERS , PRINT THE MESSAGE 'NOT VALID SORRY '"
        "IF THE PERSON on USERS IS NOT MARKED PRESENT ON DATA,THEN COUNT AS ABSENT SUCH THAT THE PERSON MUST BE ON users LIST attached"
        "DONOT RESPOND ANY ANSWERS OTHER THAN RELATED TO THE FILES GIVEN TO YOU."
        "IF USER ASKS FOR ANYTHING NOT RELATED TO THE FILES or 2FA, JUST SAY 'DUE TO BEING PROGRAMMED BY SAMIP REGMI , NAYAN NEMBANG AND RAJU BHETWAL FOR THEIR PROJECT 2FA I AM ONLY ABLE TO HELP U ON ATTENDENCE OR RECORDS QUERY  '."
        "IF USER ASKS WHO MADE U ANSWER 'I AM MADE BY SAMIP REGMI , NAYAN NEMBANG AND RAJU BHETWAL FOR THEIR PROJECT 2FA'."
        "IF USER ASKS ABOUT 2FA ANSWER '2FA IS A PROJECT MADE BY SAMIP REGMI , NAYAN NEMBANG AND RAJU BHETWAL WHICH IS AN AUTHENTICATION SYSTEM USING FACIAL RECOGNITION AND FREQUENCY RECOGNITION , CURRENTLY RECORD KEEPING IS BEING USED FOR DEMO AND PROTOTYPING THE USE CASE'."
    )

    full_prompt = instruction + "\n\n" + prompt
    response = model.generate_content([full_prompt, content, users])
    return response.text.strip()

def generate_otp():
    otp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(otp_secret, interval=30)
    return totp, totp.now()


def send_email(sender_email, sender_password, receiver_email, subject, body, html=False):
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    if html:
        part = MIMEText(body, "html")
    else:
        part = MIMEText(body, "plain")

    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def readfile(file):
    try:
        with open(f"{file}.csv") as f:
            return f.read()
    except Exception as e:
        return f'Data not found for date {file}'


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False



messages=[]
def handle_user_connection(connection: socket.socket, address: str) -> None:
    try:
        # SERVER SENDS MESSAGE JULY 17
        connection.send(f"""
+----------------------+
|     CONNECTED !      |
|     2FA SYSTEMS      |
|ENTER YOUR CREDENTIALS|
+----------------------+
""".encode())
        connection.send(b"USERNAME >>:")
        user_username = connection.recv(1024).decode().strip()
        connection.send(b"SECRET CODE >>:")
        user_password = connection.recv(1024).decode().strip()
        user_found = False
        users = read_json()
        for user in users:
            if user['name'] == user_username and user['secret'] == user_password:
                current_user = user 
                user_found = True
                break

        if user_found:
            connection.send(f"WELCOME {user_username}\n".encode())
        else:
            connection.send(b"Invalid username or password. Exiting.\n")
            remove_connection(connection)
            return

        # ramro dekhinxa cool :) :) :)
        command_counter = int(0)
        while True:

                connection.send(f"[{command_counter}][{user_username}]@2FA :".encode())
                msg = connection.recv(1024)
                command_counter += 1
                if msg:
                    decoded = msg.decode().strip()

                    print(f'{address[0]}:{address[1]} - {decoded}')
                    if is_valid_date(decoded):
                        # readfile(decoded)
                        connection.send(f"\n-----\n[*] FROM 2FA \n{readfile(decoded)}\n-----\n".encode())
                    elif decoded.lower() == '2fa':
                        connection.send(f"\n-----\n[*] FROM 2FA \n{readfile(decoded)}\n-----\n".encode())
                    elif decoded.lower() == 'help':
                        connection.send("\n----------\nFROM 2FA > made by 2FA systems 2025\n1. 2fa - list data of 2fa.csv\n2. <date> - list attendence of that particular date\n3. ask - ask queries to AI related to attendence\n4. mark <email> - mark attendance for a user\n5. msee - list all messages\n6. help - show this help message\n7. exit".encode())
                    elif decoded.lower() == 'ask':
                        connection.send("ASK::".encode())     
                        query = f"Qurey:{connection.recv(1024).decode().strip()}\nusername of person giving you query:{user_username}"
                        answer = to_model(query)
                        connection.send(f"{answer}\n".encode())
                    elif decoded.lower() == 'exit':
                        connection.send(b"Goodbye! 2FA Systems , Stay Authenticated :)\n")
                        remove_connection(connection)
                    elif decoded.lower()=='msee':
                        if messages:
                            connection.send(("\n***MESSAGES***\n"+"\n".join(messages)+"\n***END***\n").encode())
                        else:
                            connection.send(b"No messages yet.\n")
                    elif decoded.lower()=='msend':
                        print(messages)
                        connection.send(b"MESSAGE>>:")
                        # msg_txt=connection.recv(1024).decode().strip()
                        # if msg_txt:
                        #     full_msg=f"{user_username} > {msg_txt}"
                        #     messages.append(full_msg)
                        #     connection.send(b"Message sent.\n")
                        # else:
                        #     connection.send(b"Empty message not sent.\n")
                        if user_username == 'samipregmi' or user_username == 'nayannembang' or user_username == 'rajubhetwal':
                            msg_txt=connection.recv(1024).decode().strip()
                            if msg_txt:
                                full_msg=f"{user_username} > {msg_txt}"
                                messages.append(full_msg)
                                connection.send(b"Message sent.\n")
                            else:
                                connection.send(b"Empty message not sent.\n")
                        else:
                            connection.send(b"Only admins can send messages.\n")
                    elif decoded.lower() == "mark":
                        email = current_user['email']
                        df = pd.read_csv('2fa.csv')
                        # connection.send(b"Enter Email to receive OTP: ")
                        # email = connection.recv(1024).decode().strip()
                        # if email:
                        exists = ((df['name'] == user_username) & (df['date'] == today_date)).any()
                        print("exist:",exists)
                        if email and email !='NULL' and not exists:
                            totp,otp  = generate_otp()
                            # ----------------------------------------
                            # OLD CODE
                            # send_email(MAIL_USERNAME, MAIL_PASSWORD, email, "2FA OTP", f"FROM 2FA SYSTEMS\nYour OTP code is: {otp}\nOTP resets 1 minute after generation\n@2FA samipregmi, nayannembang, rajubhetwal\n")
                            
                            # ------------------------------------------
                            
                            send_email(
                                MAIL_USERNAME,
                                MAIL_PASSWORD,
                                email,
                                "Your 2FA Verification Code",
                                f"""\
                            <html>
                            <body>
                                <p>Namaste <b>{user_username}</b></p>
                                <p>Your One-Time Password (OTP) for 2FA TCP server is:</p>
                                <p style="font-size:18px;">
                                <b>{otp}</b>
                                </p>
                                <p>⚠️ This code will expire in 1 minute for security reasons</p>
                                <p>If you did not request this code, please ignore this email</p>
                                <hr>
                                <h1>2FA Systems</h1>
                                <p>Developed by Samip Regmi, Nayan Nembang, and Raju Bhetwal</p>
                            </body>
                            </html>
                            """,
                                html=True  
                            )

                            otp_generated_time = time.time()
                            connection.send(f"OTP sent to {email}. Please enter the OTP\nOTP ?".encode())
                            user_otp = connection.recv(1024).decode().strip()
                            current_time =  time.time()
                            # 60 second vanda besi time vayo vane ,invalidate that code
                            if current_time - otp_generated_time > 60:
                                connection.send(b"OTP expired. Please try again.\n")
                            elif user_otp == otp:
                                if ReportWrite.write_data(user_username) == 100:
                                    ReportWrite.report()
                                    print('--writing image---')
                                    ReportWrite.write_image(user_username, date.today().isoformat(), timestamp=datetime.now().isoformat())
                                    # save to sql
                                    ReportWrite.save_to_sql(att_date=date.today().isoformat())
                                    connection.send(b"Success, marked attendance.\n")
                                else:
                                    connection.send(b"Info, attendance already marked.\n")
                                    ReportWrite.report()
                            else:
                                connection.send(b"Invalid OTP.\n")
                        else:
                            connection.send(b"EXISTS Info, attendance already marked.\n")
                    else:
                        connection.send(f"[!!!]2FA WARNING\n***Unknown Command {decoded}***\nPlease dont use Capital letters\nDont use spaces\n".encode())
                        continue
                        # remove_connection(connection)
                        # break

                    #JULY 17 SAMIP REGMI EDITED ---- 
                    # Broadcast message to other users (optional)
                    # msg_to_send = f'From {address[0]}:{address[1]} - {decoded}'
                    # broadcast(msg_to_send, connection)

                else:
                    remove_connection(connection)
                    break

    except Exception as e:
        print(f'Error to handle user connection: {e}')
        remove_connection(connection)
        return



def remove_connection(conn: socket.socket) -> None:

    if conn in connections:
        conn.close()
        connections.remove(conn)


def server() -> None:

    LISTENING_PORT = 12000
    
    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', LISTENING_PORT))
        socket_instance.listen(4)

        print('Server running!')
        
        while True:

            socket_connection, address = socket_instance.accept()
            connections.append(socket_connection)

            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()
