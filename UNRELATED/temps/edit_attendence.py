import csv
import datetime
import ReportWrite
def remove_line(date, name):
    with open('2fa.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open('2fa.csv', 'w', encoding='utf-8') as file:
        for line in lines:
            parts = line.strip().split(',')
            if not (len(parts) >= 2 and parts[0] == date and parts[1] == name):
                file.write(line)


user_file = input("Enter the date you want to edit (YYYY-MM-DD): ")
with open(f"{user_file}.csv", "r") as file:
    content = file.read()
    print(content)
choose = input("1 to edit mark present or 2 to edit mark absent: ")
if choose == "1":
    # ask for name and then ask for date , if not given date then use date.now()
    name = input("Enter the name of the person to mark present: ")
    timestamp = input("Enter the timestamp (YYYY-MM-DD) or press Enter to use today's date: ")
    if not timestamp:
        timestamp = datetime.datetime.now().isoformat()

    ReportWrite.write_data(timestamp=timestamp, name=name, today=user_file, attendence="present")
    ReportWrite.report(attendance_date=user_file)
elif choose == "2":
    name = input("Enter the name of the person to mark absent: ")
    remove_line(user_file, name)
    ReportWrite.report(attendance_date=user_file)

else:
    print("Invalid choice. Please enter 1 or 2.")


