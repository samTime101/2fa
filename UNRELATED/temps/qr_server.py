# app.py
from flask import Flask, request, render_template_string
import numpy as np
import sounddevice as sd
import hashlib
import datetime
import time
import json
from scipy.signal import periodogram
import random
import qrcode

app = Flask(__name__)
otp_store = {}

with open('user.json', 'r') as f:
    users = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def otp_page():
    user = request.args.get('user')
    if not user:
        return "Missing user", 400

    if request.method == 'POST':
        entered = request.form.get('otp')
        expected = otp_store.get(user)
        print(f"Entered OTP for {user}: {entered}")
        print(f"Expected OTP for {user}: {expected}")
        if entered == expected:
            print('[SERVER] OTP verified successfully!')
            return f"<h2>✅ OTP verified for {user}!</h2>"
        else:
            return f"<h2>❌ Incorrect OTP for {user}!</h2>"

    return render_template_string('''
        <h3>Enter OTP for {{user}}</h3>
        <form method="post">
            <input name="otp" placeholder="Enter OTP" />
            <input type="submit" value="Verify" />
        </form>
    ''', user=user)

def set_otp(user, otp):
    otp_store[user] = str(otp)
    print(f"[SERVER] OTP set for {user}: {otp}")

# --- Frequency-based Auth ---
sample_rate = 44100
duration = 2.0
tolerance = 0.0

def get_stable_random_number():
    now = datetime.datetime.now()
    seed = int(now.strftime("%Y%m%d%H%M"))
    random.seed(seed)
    return random.randint(100, 999)

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
        if abs(peak_freq - expected_freq) <= tolerance:
            print(f"✅ Match found for {user_data['name']}!")

            return (True , user_data['name'])

    print("❌ No match found — possibly spoofed or expired.")
    return (False , "")

def generate_dynamic_frequency(user_data):
    base_freq = user_data["frequency"]
    secret_key = user_data["secret"]
    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    timestamp_str = now.isoformat() + 'Z'
    combo = f"{secret_key}-{timestamp_str}"
    hash_digest = hashlib.sha256(combo.encode()).hexdigest()
    hash_val = int(hash_digest[-4:], 16)
    bias = hash_val % 20
    return base_freq + bias + now.minute

def detect_frequency():
    print("🎤 Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()
    frequencies, power = periodogram(audio.flatten(), sample_rate)
    peak_freq = frequencies[np.argmax(power)]
    return peak_freq

def qr_prompt(person):
    ip = "192.168.1.84"
    url = f"http://{ip}:5000/?user={person}"
    print("📱 Scan this QR on your phone:")
    qr = qrcode.QRCode(box_size=3, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii()
def main():
    '''
    main():
    program entry point
    '''
    while True:
        detected_freq = detect_frequency()
        user_detected, user_name = verify_frequency(detected_freq)
        if not user_detected:
            print("No valid attendance found.")
            continue
        else:
            print(f"Detected user: {user_name}")
            otp = get_stable_random_number()
            set_otp(user_name, otp)
            qr_prompt(user_name)

        print("Waiting for OTP verification...")
        time.sleep(5)



if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    time.sleep(1)
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Exiting...")
