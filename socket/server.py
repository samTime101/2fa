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
from analysis import to_model
import pandas as pd
connections = []
load_dotenv()




today_date = date.today().isoformat()  


MAIL_USERNAME= os.getenv('MAIL_USERNAME')
MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER= os.getenv('MAIL_SERVER')

JSON_FILE_PATH = 'user.json'

with open(JSON_FILE_PATH, 'r') as f:
    users = json.load(f)


def generate_otp():
    otp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(otp_secret, interval=30)
    return totp, totp.now()

def send_email(sender_email, sender_password, receiver_email, subject, message_body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")


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
                    elif decoded == '2fa':
                        connection.send(f"\n-----\n[*] FROM 2FA \n{readfile(decoded)}\n-----\n".encode())
                    elif decoded == 'help':
                        connection.send("\n----------\nFROM 2FA > made by SamipRegmi 2025\n1. 2fa - list data of 2fa.csv\n2. <date> - list attendence of that particular date\n3. ask - ask queries to AI related to attendence\n4. help - help related to this application\n".encode())   
                    elif decoded == 'ask':
                        connection.send("ASK::".encode())     
                        query = connection.recv(1024).decode().strip()
                        answer = to_model(query)
                        connection.send(f"{answer}\n".encode())
                    elif decoded == 'exit':
                        connection.send(b"Goodbye!\n")
                        remove_connection(connection)
                    elif decoded == "mark":
                        email = current_user['email']
                        df = pd.read_csv('2fa.csv')
                        # connection.send(b"Enter Email to receive OTP: ")
                        # email = connection.recv(1024).decode().strip()
                        # if email:
                        exists = ((df['name'] == user_username) & (df['date'] == today_date)).any()
                        print("exist:",exists)
                        if email and email !='NULL' and not exists:
                            totp,otp  = generate_otp()
                            send_email(MAIL_USERNAME, MAIL_PASSWORD, email, "2FA OTP", f"FROM 2FA SYSTEMS\nYour OTP code is: {otp}\nOTP resets 1 minute after generation\n@2FA samipregmi, nayannembang, rajubhetwal\n")
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
                                    connection.send(b"Success, marked attendance.\n")
                                else:
                                    connection.send(b"Info, attendance already marked.\n")
                                    ReportWrite.report()
                            else:
                                connection.send(b"Invalid OTP.\n")
                        else:
                            connection.send(b"Info, attendance already marked.\n")
                    else:
                        connection.send("Unknown command. Exiting.".encode())
                        remove_connection(connection)
                        break

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