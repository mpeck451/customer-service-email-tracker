import csv
import sqlite3
import math

print("Script Start...")
csv_email_data = []
csv_department_data = []

print("Opening csv files...")
with open('../../../database/implementation-department.csv') as department_data:
    file_reader = csv.DictReader(department_data)
    for row in list(file_reader):
        new_row = []
        for item in row.items():
            new_row.append(item[1])
        csv_department_data.append(tuple(new_row))
with open('../../../database/customer-emails.csv') as customer_emails:
    file_reader = csv.DictReader(customer_emails)
    for row in list(file_reader):
        new_row = []
        for item in row.items():
            new_row.append(item[1])
        csv_email_data.append(tuple(new_row))

print("Connecting to sqlite3 database...")

connection = sqlite3.connect("../../../database/implementation.db")
cursor = connection.cursor()

print("Updating database tables...")
#cursor.execute("""CREATE TABLE implementation_specialists (
#    trainer_id INTEGER,
#    first_name TEXT,
#    last_name TEXT,
#    position TEXT,
#    start_date DATE,
#    work_from_home INTEGER)""")
#cursor.executemany("""INSERT INTO implementation_specialists VALUES (?, ?, ?, ?, ?, ?)""", csv_department_data)

#cursor.execute("""CREATE TABLE customer_emails (
#    email_id INTEGER,
#    datetime_received INTEGER,
#    datetime_assigned INTEGER,
#    trainer_id INTEGER,
#    sender_name TEXT,
#    company TEXT,
#    customer_id INTEGER,
#    type TEXT
#)""")
#cursor.executemany("INSERT INTO customer_emails VALUES (?, ?, ?, ?, ?, ?, ?, ?)", csv_email_data)

all_trainers = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
all_emails = cursor.execute("SELECT * from customer_emails").fetchall()

individual_totals = cursor.execute("""
    SELECT implementation_specialists.first_name, implementation_specialists.last_name, COUNT(customer_emails.trainer_id) 
    FROM implementation_specialists 
    LEFT JOIN customer_emails 
    ON implementation_specialists.trainer_id = customer_emails.trainer_id 
    GROUP BY implementation_specialists.last_name 
    ORDER BY COUNT(customer_emails.trainer_id) DESC""").fetchall()

tas_total =cursor.execute("""
    SELECT COUNT(*)
    FROM customer_emails
    WHERE type = 'TAS'
""").fetchall()

hospital_total =cursor.execute("""
    SELECT COUNT(*)
    FROM customer_emails
    WHERE type = 'Hospital'
""").fetchall()

print("Closing database connection...")
connection.commit()
connection.close()

print("Generating reports...")
print("========================")

email_total = len(all_emails)
print(f"Email Totals: {email_total}")


print(f"TAS: {tas_total[0][0]} ({math.floor((tas_total[0][0]/email_total)*100)}%)")
print(f"Hospital: {hospital_total[0][0]} ({math.floor((hospital_total[0][0]/email_total)*100)}%)")

for trainer in individual_totals:
    print(f'{trainer[0]} {trainer[1]}: {trainer[2]}')


print("...Script End")