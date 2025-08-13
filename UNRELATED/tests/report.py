import pandas as pd
import json
import matplotlib.pyplot as plt

with open('user.json', 'r') as f:
    users_data = json.load(f)

df = pd.read_csv('2fa.csv')

attendance_date = '2025-07-05' 


present_users = df[(df['date'] == attendance_date) & (df['attendance'] == 'present')]

all_users_list = [user['name'] for user in users_data]

present_users_list = present_users['name'].tolist()
print(present_users_list)
print(all_users_list)



absent_users_list = list(set(all_users_list) - set(present_users_list))

print(f"Present Users on {attendance_date}: {present_users_list}")
print(f"Absent Users on {attendance_date}: {absent_users_list}")

attendance_count = {
    'Present': len(present_users_list),
    'Absent': len(absent_users_list)
}


with open('report.csv','w') as f:
    f.write("status,name,date\n") 
    for user in present_users_list:  
        f.write(f"present,{user},{attendance_date}\n")
    for user in absent_users_list:
        f.write(f"absent,{user},{attendance_date}\n")
    
