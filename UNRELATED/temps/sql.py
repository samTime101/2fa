# JULY 15
# SAMIP REGMI
# SQL DATABASE MA SAVE GARNE


import csv
import mysql.connector



# table_name = "attendence_2025-07-15"

# cursor.execute(f"""
#     CREATE TABLE IF NOT EXISTS {table_name} (
#         status VARCHAR(20),
#         name VARCHAR(50),
#         date DATE,
#         timestamp VARCHAR(100)
#     )
# """)

# with open("2025-07-15.csv", newline='') as csvfile:
#     reader = csv.reader(csvfile)
#     next(reader) 

#     for row in reader:
#         cursor.execute(f"""
#             INSERT INTO {table_name} (status, name, date, timestamp)
#             VALUES (%s, %s, %s, %s)
#         """, row)

# conn.commit()
# conn.close()

# print('done')

def save_to_sql(date):
    table_name = date.replace('-','_')
    conn = mysql.connector.connect(
    host="localhost",
    user="root",           
    password="",           
    database="2fa"     

    # host = 'sql12.freesqldatabase.com',
    # database = 'sql12790150',
    # user='sql12790150',
    # password = 'MYgf12FRGW',
    # port = 3306
)
    cursor = conn.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        status VARCHAR(20),
        name VARCHAR(50),
        date DATE,
        timestamp VARCHAR(100)
    )
""")

    with open(f'{date}.csv',newline= '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            cursor.execute(f"""
            insert into {table_name} values (%s,%s,%s,%s);

""",row)
        conn.commit()
        conn.close()
        print('done')

save_to_sql('2025-07-15')

