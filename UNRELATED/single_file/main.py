from flask import Flask
from flask_cors import CORS
from l import login_bp       
from d import attendance_bp  
app = Flask(__name__)
CORS(app)

app.secret_key = 'admin'

app.register_blueprint(attendance_bp)
app.register_blueprint(login_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)