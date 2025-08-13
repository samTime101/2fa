from flask import Flask, render_template
from flask_socketio import SocketIO, send
import socket
import threading

TCP_HOST = '127.0.0.1'
TCP_PORT = 12000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

tcp_conn = None

def tcp_listener():
    """Read from TCP server and send to browser."""
    global tcp_conn
    while True:
        try:
            data = tcp_conn.recv(1024)
            if not data:
                break
            socketio.send(data.decode())
        except:
            break

@socketio.on('connect')
def handle_connect():
    global tcp_conn
    print("Web client connected")

    tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_conn.connect((TCP_HOST, TCP_PORT))

    threading.Thread(target=tcp_listener, daemon=True).start()

@socketio.on('message')
def handle_message(msg):
    global tcp_conn
    if tcp_conn:
        tcp_conn.send(msg.encode())

@app.route('/')
def index():
    return render_template('socket.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
