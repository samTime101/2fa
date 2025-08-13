import pandas as pd
import requests
import io
import datetime


def read_data(time):
    url = f'https://samip.pythonanywhere.com/space/2fa/{time}'
    response = requests.get(url)
    data = response.json() 

    csv_content = data['file']
    df = pd.read_csv(io.StringIO(csv_content))

    print(df)



read_data(datetime.date.today().isoformat())