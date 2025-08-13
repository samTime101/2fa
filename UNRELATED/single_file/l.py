from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
import json, os, base64, datetime
from dotenv import load_dotenv
import google.generativeai as genai

login_bp = Blueprint('loginmanager', __name__)

load_dotenv()
genai.configure(api_key=os.getenv('USING_GEMINI_KEY'))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
today = datetime.date.today().isoformat()


@login_bp.app_template_global()
def load_users():
    with open('user.json', 'r') as f:
        return json.load(f)

@login_bp.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('loginmanager.admin_dashboard' if session['user']['role'] == 'admin' else 'loginmanager.user_dashboard'))
    return redirect(url_for('loginmanager.login'))

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name'].strip().lower()
        secret = request.form['secret']

        if name == "admin" and secret == "admin":
            session['user'] = { 'name': 'admin', 'role': 'admin' }
            return redirect(url_for('loginmanager.admin_dashboard'))

        users = load_users()
        for user in users:
            if user['name'] == name and user['secret'] == secret:
                session['user'] = { 'name': name, 'role': 'user','secret': user['secret'], 'frequency': user.get('frequency', 0) }
                return redirect(url_for('loginmanager.user_dashboard'))

        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@login_bp.route('/signup', methods=['GET', 'POST'])
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
    if any(user['name'] == name or user['secret'] == secret for user in users):
        return jsonify({'error': 'User already exists'}), 400

    student_id_folder = './student_id'
    os.makedirs(student_id_folder, exist_ok=True)
    with open(os.path.join(student_id_folder, f"{name}.png"), "wb") as f:
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

@login_bp.route('/csv/2fa.csv')
def serve_2fa_csv():
    user = session.get('user')
    if not user or user.get('role') != 'user':
        abort(403)
    return send_file('2fa.csv', mimetype='text/csv')

@login_bp.route('/csv/<filename>')
def serve_csv(filename):
    user = session.get('user')
    if not user or user.get('role') != 'admin' or not filename.endswith('.csv'):
        abort(403)

    safe_path = os.path.abspath(filename)
    if not safe_path.startswith(os.getcwd()) or not os.path.isfile(safe_path):
        abort(404)

    return send_file(safe_path, mimetype='text/csv')

@login_bp.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('loginmanager.login'))
    return render_template('admin.html', user=session['user'])

@login_bp.route('/user')
def user_dashboard():
    if 'user' not in session or session['user']['role'] != 'user':
        return redirect(url_for('loginmanager.login'))
    return render_template('user.html', user=session['user'])

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('loginmanager.login'))

def to_model(prompt):
    with open('2fa.csv', 'r') as f1, open('user.json', 'r') as f2:
        content = f1.read()
        users = f2.read()

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

@login_bp.route('/analysis', methods=['POST'])
def get_response():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        abort(403)

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"response": "No prompt provided."})

    return jsonify({"response": to_model(prompt)})
