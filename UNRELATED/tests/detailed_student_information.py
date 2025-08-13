import csv
import json
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
username = input("Enter username: ").strip()
title, present_info, absent_info = get_attendance_info(username)

print(f"\n{title}")
print("\nPresent Information:")
for record in present_info:
    print(f"Date: {record['date']}, Timestamp: {record['timestamp']}")

print("\nAbsent Information:")
for date in absent_info:
    print(f"Date: {date}")
