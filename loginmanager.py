from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from flask import send_file, abort
import os
from dotenv import load_dotenv
import google.generativeai as genai
import datetime
# import csv
from flask_socketio import SocketIO, send
import socket
import threading
import os
from flask import send_from_directory
load_dotenv()
genai.configure(api_key=os.getenv('USING_GEMINI_KEY'))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_SECRET = os.getenv('ADMIN_SECRET')
app = Flask(__name__)
app.secret_key = 'admin'  
from flask_cors import CORS
import base64
from io import BytesIO
from PIL import Image
import csv
CORS(app)

def load_users():
    with open('user.json', 'r') as f:
        return json.load(f)

@app.route('/')
def home():
    if 'user' in session:
        if session['user']['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name'].strip().lower()
        secret = request.form['secret']

        if name == ADMIN_USERNAME and secret == ADMIN_SECRET:
            session['user'] = { 'name': 'admin', 'role': 'admin' }
            return redirect(url_for('admin_dashboard'))

        users = load_users()
        for user in users:
            if user['name'] == name and user['secret'] == secret:
                session['user'] = { 'name': name, 'role': 'user','secret': user['secret'], 'frequency': user.get('frequency', 0) }
                return redirect(url_for('user_dashboard'))

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    data = request.get_json()

    name = data.get('username', '').strip().lower()
    secret = data.get('secret', '').strip()
    email = data.get('email', '').strip()
    photo_base64 = data.get('photo')

    if not name or not secret or not email or not photo_base64:
        return jsonify({'error': 'All fields are required'}), 400

    users = load_users()
    for user in users:
        if user['name'] == name or user['secret'] == secret:
            return jsonify({'error': 'User already exists'}), 400

    student_id_folder = './student_id'
    os.makedirs(student_id_folder, exist_ok=True)
    photo_path = os.path.join(student_id_folder, f"{name}.png")
    with open(photo_path, "wb") as f:
        f.write(base64.b64decode(photo_base64))

    new_user = {
        "name": name,
        "frequency": (users[-1]['frequency'] + 20) if users else 400,
        "secret": secret,
        "email": email
    }

    users.append(new_user)
    with open('user.json', 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({'success': 'User created successfully'})

@app.route('/csv/2fa.csv')
def serve_2fa_csv():
    user = session.get('user')
    print(f"user {user}")
    if not user or user.get('role') != 'user':
        abort(403)

    file_path = os.path.join(app.root_path, '2fa.csv')
    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path, mimetype='text/csv')



@app.route('/csv/<filename>')
def serve_csv(filename):
    user = session.get('user')
    print(f"user {user}")
    if not user or user.get('role') != 'admin':
        abort(403)  

    if not filename.endswith('.csv'):
        abort(403)

    safe_path = os.path.abspath(os.path.join(app.root_path, filename))
    if not safe_path.startswith(app.root_path) or not os.path.isfile(safe_path):
        abort(404)

    return send_file(safe_path, mimetype='text/csv')


@app.route('/image/<filename>')
def serve_image(filename):
    user = session.get('user')
    print(f"user {user}")
    if not user or user.get('role') != 'admin':
        abort(403)

    if not filename.endswith('.png'):
        abort(403)

    safe_path = os.path.abspath(os.path.join(app.root_path, 'image_logs', filename))
    print(safe_path)
    if not safe_path.startswith(app.root_path) or not os.path.isfile(safe_path):
        abort(404)

    return send_file(safe_path, mimetype='image/png')


@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', user=session['user'])

@app.route('/user')
def user_dashboard():
    if 'user' not in session or session['user']['role'] != 'user':
        return redirect(url_for('login'))
    with open('user.json', 'r') as f:
        users = json.load(f)

    user = None
    for u in users:
        if u['name'] == session['user']['name']:
            user = u
            break

    if not user:
        return render_template('404.html'), 404

    # Check if photo exists
    user['photo'] = None
    for ext in ['.png', '.jpeg', '.jpg']:
        img_path = os.path.join(STUDENT_ID_FOLDER, user['name'] + ext)
        if os.path.exists(img_path):
            user['photo'] = user['name'] + ext
            break
    print(session['user'])
    return render_template('user.html', user=session['user'] , user_photo = user)

            

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



today = datetime.date.today().isoformat()


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
def to_analysis_model(prompt, present_info, absent_info):
    instruction = (
        "You are an attendance analysis assistant. "
        "Analyze the attendance data provided and give a clear, concise, and direct report. "
        "Do not start with phrases like 'Attendance Analysis for...' or 'Feedback:'. "
        "Do not repeat the user's name unnecessarily. "
        "Summarize patterns, gaps, and trends in attendance. "
        "Provide actionable feedback in a professional, encouraging tone. "
        "Format your output using Markdown: "
        "- Use headings, bold, italics, line breaks, and lists as appropriate. "
        "- Do not use code blocks or tables. "
    )

    full_prompt = instruction + "\n\n" + prompt
    response = model.generate_content([full_prompt, json.dumps(present_info), json.dumps(absent_info)])
    return response.text.strip()


@app.route('/analysis', methods=['POST'])
def get_response():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        abort(403)  

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"response": "No prompt provided."})
    answer = to_model(prompt)
    return jsonify({"response": answer})

# 
# AUG 9 2025
# CUSTOM 404 ERROR HANDLER
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


import ReportWrite  

def remove_line(date, name):
    try:
        with open('2fa.csv', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open('2fa.csv', 'w', encoding='utf-8') as file:
            for line in lines:
                parts = line.strip().split(',')
                if not (len(parts) >= 2 and parts[0] == date and parts[1] == name):
                    file.write(line)
    except FileNotFoundError:
        return "Error: 2fa.csv not found."
    except Exception as e:
        return f"Error while removing line: {e}"
    return None


@app.route('/admin/attendance', methods=['GET', 'POST'])
def admin_attendance():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_date = request.form['date'].strip()
        csv_path = f"{selected_date}.csv"

        if not os.path.exists(csv_path):
            return render_template('attendance.html', error=f"File {csv_path} not found.")

        with open(csv_path, "r", encoding="utf-8") as file:
            csv_content = file.read()

        return render_template('attendance_edit.html', date=selected_date, csv_content=csv_content)

    return render_template('attendance.html')


@app.route('/admin/attendance/update', methods=['POST'])
def admin_attendance_update():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    date = request.form['date']
    name = request.form['name'].strip()
    choice = request.form['choice']
    timestamp = request.form.get('timestamp') or datetime.datetime.now()
    print(f"date: {date}, name: {name}, choice: {choice}, timestamp: {timestamp}")
    if choice == "1":
        ReportWrite.write_data(timestamp=timestamp, name=name, today=date, attendence="present")
        ReportWrite.save_to_sql(att_date=date)
        ReportWrite.write_image(name, date, timestamp,server_message="Attendence done\nDone By ADMIN\n")
    else:
        remove_line(date, name)
        image_path = os.path.join(app.root_path, 'image_logs', f"{date}_{name}.png")
        if os.path.exists(image_path):
            os.remove(image_path)
        ReportWrite.save_to_sql(att_date=date)
    ReportWrite.report(attendance_date=date)
    ReportWrite.save_to_sql(att_date=date)
    return redirect(url_for('admin_attendance'))


# user Info page it loads user data from user.json and their photos from student_id folder


STUDENT_ID_FOLDER = os.path.join(os.getcwd(), 'student_id')

@app.route('/student_id/<filename>')
def student_id_file(filename):
    # make it only accessible to admin
    # if 'user' not in session or session['user']['role'] != 'admin':
    #     return redirect(url_for('login'))
    return send_from_directory(STUDENT_ID_FOLDER, filename)

@app.route('/admin/user_info', methods=['GET'])
def admin_user_info():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    with open('user.json', 'r') as f:
        users = json.load(f)

    for user in users:
        for ext in ['.png', '.jpeg', '.jpg']:
            img_path = os.path.join(STUDENT_ID_FOLDER, user['name'] + ext)
            if os.path.exists(img_path):
                user['photo'] = user['name'] + ext
                break
        else:
            user['photo'] = None  

    return render_template('user_info.html', users=users ,no_of_users=len(users))


def get_attendance_info(username, csv_file='2fa.csv', json_file='user.json'):
    attendance_data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attendance_data.append(row)
    with open(json_file, 'r') as f:
        users = json.load(f)

    user_names = [user['name'] for user in users]
    if username not in user_names:
        return f"User '{username}' not found.", [], []
    all_dates = sorted(list({row['date'] for row in attendance_data}))
    present_dates = sorted([row['date'] for row in attendance_data if row['name'] == username and row['attendance'] == 'present'])
    absent_dates = [date for date in all_dates if date not in present_dates]
    student_present_info = []
    for date in present_dates:
        timestamp = next((row['timestamp'] for row in attendance_data if row['name']==username and row['date']==date), "")
        student_present_info.append({'date': date, 'timestamp': timestamp})
    student_absent_info = absent_dates

    return f"Attendance info for '{username}'", student_present_info, student_absent_info


# INFORMATION REGARDING INVIDIDUAL USERS
@app.route('/admin/user_info/<username>', methods=['GET'])
def admin_user_info_detail(username):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    with open('user.json', 'r') as f:
        users = json.load(f)
    user = next((u for u in users if u['name'] == username), None)
    if not user:
        return render_template('404.html'), 404
    user['photo'] = None  
    if user:
        for ext in ['.png', '.jpeg', '.jpg']:
            img_path = os.path.join(STUDENT_ID_FOLDER, user['name'] + ext)
            if os.path.exists(img_path):
                user['photo'] = user['name'] + ext
                break
    title, present_info, absent_info = get_attendance_info(username)
    # ai_analysis = to_analysis_model(f"Analyze the attendance data for {username} and provide feedback.", present_info=present_info, absent_info=absent_info)
    return render_template('user_info_detail.html', user=user, title=title, present_info=present_info, absent_info=absent_info)

# ROUTE TO ANALYZE USER DATA
@app.route('/admin/user_info/analysis', methods=['POST'])
def admin_user_info_analysis():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    data = request.get_json()
    username = data.get('username', '').strip().lower()
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    title, present_info, absent_info = get_attendance_info(username)
    if isinstance(title, str) and title.startswith("User"):
        return jsonify({'error': title}), 404

    ai_analysis = to_analysis_model(f"Analyze the attendance data for {username} and provide feedback.", present_info=present_info, absent_info=absent_info)
    return jsonify({'analysis': ai_analysis})


# ALLOW USER TO EDIT THEIR PROFILE PHOTO
@app.route('/user/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session or session['user']['role'] != 'user':
        return redirect(url_for('login'))

    with open('user.json', 'r') as f:
        users = json.load(f)

    current_user = next((u for u in users if u['name'] == session['user']['name']), None)
    if not current_user:
        return render_template('404.html'), 404

    if request.method == 'GET':
        current_user['photo'] = None
        for ext in ['.png', '.jpg', '.jpeg']:
            img_path = os.path.join(STUDENT_ID_FOLDER, current_user['name'] + ext)
            if os.path.exists(img_path):
                current_user['photo'] = current_user['name'] + ext
                break
        return render_template('edit_profile.html', user=current_user)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    updated_email = data.get('email', '').strip()
    photo_base64 = data.get('photo', '').strip()

    if updated_email:
        if any(u['email'] == updated_email and u['name'] != current_user['name'] for u in users):
            return jsonify({'error': 'Email already in use'}), 400
        current_user['email'] = updated_email
        session['user']['email'] = updated_email

    if photo_base64:


        try:
            header, encoded = photo_base64.split(',', 1)
            img_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_data))
            ext = 'png'
            save_path = os.path.join(STUDENT_ID_FOLDER, current_user['name'] + '.' + ext)
            img.save(save_path)
        except Exception as e:
            return jsonify({'error': f'Failed to save photo: {str(e)}'}), 500

    with open('user.json', 'w') as f:
        json.dump(users, f, indent=2)

    return jsonify({'success': True, 'email': updated_email if updated_email else current_user['email']})


# ADDED ON AUG 11, 2025

TCP_HOST = 'localhost'
TCP_PORT = 12000
print(f"socket: {TCP_HOST}:{TCP_PORT}")
socketio = SocketIO(app)
user_tcp_conns = {} 


def tcp_listener(sid, tcp_conn):
    while True:
        try:
            data = tcp_conn.recv(1024)
            if not data:
                break
            socketio.send(data.decode(), to=sid)
        except:
            break
    tcp_conn.close()
    user_tcp_conns.pop(sid, None)
import time
@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print(f"Web client connected: {sid}")

    username = session['user']['name']
    secret = session['user']['secret']

    tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_conn.connect((TCP_HOST, TCP_PORT))
    user_tcp_conns[sid] = tcp_conn

    def tcp_listener_and_auto_login(sid, tcp_conn,username, secret):
        try:
            buffer = ""
            while True:
                data = tcp_conn.recv(1024)
                if not data:
                    break

                text = data.decode()
                buffer += text

                socketio.send(text, to=sid)

                if "USERNAME" in buffer.upper():
                    tcp_conn.send((username + "\n").encode())
                    buffer = ""
                elif "SECRET" in buffer.upper():
                    tcp_conn.send((secret + "\n").encode())
                    buffer = ""

        except Exception as e:
            print(f"TCP listener error: {e}")
        finally:
            tcp_conn.close()
            user_tcp_conns.pop(sid, None)
    threading.Thread(
        target=tcp_listener_and_auto_login,
        args=(sid, tcp_conn, username, secret),  
        daemon=True
    ).start()


@socketio.on('message')
def handle_message(msg):
    # auto login user to tcp server
    # server firsts asks for client for username then password
    sid = request.sid
    tcp_conn = user_tcp_conns.get(sid)
    if tcp_conn:
        tcp_conn.send(msg.encode())

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Web client disconnected: {sid}")
    tcp_conn = user_tcp_conns.pop(sid, None)
    if tcp_conn:
        try:
            tcp_conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        tcp_conn.close()

@app.route('/user/socket')
def user_socket():
    if 'user' not in session or session['user']['role'] != 'user':
        return redirect(url_for('login'))
    return render_template('socket.html')


# allow favico.ico to be served
@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.root_path, 'static', 'favicon.ico'), mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5800, host='0.0.0.0')
