import csv
import datetime
import ReportWrite
import os

def remove_line(date, name):
    """Remove a line from 2fa.csv that matches the given date and name."""
    try:
        with open('2fa.csv', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open('2fa.csv', 'w', encoding='utf-8') as file:
            for line in lines:
                parts = line.strip().split(',')
                if not (len(parts) >= 2 and parts[0] == date and parts[1] == name):
                    file.write(line)
    except FileNotFoundError:
        print("Error: 2fa.csv not found.")
    except Exception as e:
        print(f"Error while removing line: {e}")

def get_input(prompt, default=None):
    """Get input with optional default value."""
    value = input(prompt).strip()
    return value if value else default

def main():
    user_file = input("Enter the date you want to edit (YYYY-MM-DD): ").strip()
    csv_path = f"{user_file}.csv"

    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            print(file.read())
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return

    choose = input("1 to mark present, 2 to mark absent: ").strip()
    if choose not in {"1", "2"}:
        print("Invalid choice. Please enter 1 or 2.")
        return

    name = input("Enter the name of the person: ").strip()
    if not name:
        print("Error: Name cannot be empty.")
        return

    if choose == "1":
        timestamp = get_input("Enter the timestamp (YYYY-MM-DD) or press Enter for today: ",
                              datetime.datetime.now().strftime("%Y-%m-%d"))
        ReportWrite.write_data(timestamp=timestamp, name=name, today=user_file, attendence="present")
    else:
        remove_line(user_file, name)

    ReportWrite.report(attendance_date=user_file)
    print("Operation completed successfully.")

if __name__ == "__main__":
    main()
