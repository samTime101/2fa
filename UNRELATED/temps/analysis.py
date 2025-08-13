# JULY 16
# SAMIP REGMI
# THE BOT - TWO CSV , QNA USING GEMINI API


# SAMIP REGMI
# JULY 17 GRAPHHHHHHH





import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

import graph
# import graph
import base64
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv('USING_GEMINI_KEY'))
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
app = Flask(__name__)
CORS(app) 

def make_graph(data='2fa.csv'):
    print('[1] generating graph')
    df = pd.read_csv(data)

    attendance_count = df['name'].value_counts()
    print(attendance_count)

    attendance_count.plot(kind='bar', color='blue')
    plt.title("Total Days Present per Person")
    plt.ylabel("Days Present")
    plt.xlabel("Name")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return img_base64 , 1

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

@app.route('/analysis', methods=['POST'])
def get_response():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"response": "No prompt provided."})
    elif prompt.lower()=='graph':
        retr_data = make_graph()
        if retr_data[1] == 1:
            return jsonify({"response": f'data:image/png;base64,{retr_data[0]}'})    
    answer = to_model(prompt)
    return jsonify({"response": answer})




if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=5700)
