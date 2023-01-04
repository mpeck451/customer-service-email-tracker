import csv
import sqlite3
import math

print("=========================")
print("SCRIPT START...")
csv_email_data = []
csv_department_data = []
def print_break():
    print("-------------------------")

print_break()
print("Connecting to sqlite3 database...")
print_break()

connection = sqlite3.connect("../../../database/implementation.db")
cursor = connection.cursor()
print(f" - {connection}")
print(f" - {cursor}")

print_break()
print("Opening csv files...")
print_break()

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

old_implementation_table = all_trainers = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
old_email_table = cursor.execute("SELECT * from customer_emails").fetchall()

new_trainers = len(csv_department_data) - len(old_implementation_table)
new_emails = len(csv_email_data) - len(old_email_table)

print(f" - {new_trainers} new trainers.")
print(f" - {new_emails} new emails.")

print_break()
print("Updating database tables...")
print_break()
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

if (new_emails > 0):
    print(f" - {new_emails} added to customer_emails table.")
    new_email_data = csv_email_data[-(new_emails):]
    for email in new_email_data:
        print(f" - {email}")
    cursor.executemany("INSERT INTO customer_emails VALUES (?, ?, ?, ?, ?, ?, ?, ?)", new_email_data)
else:
    print(" - No updates for customer_emails table.")

if (new_trainers > 0):
    print(f" - {new_trainers} added to implementation_specialists table.")
else:
    print(" - No updates for implementation_specialists table.")

print_break()
print("Executing additional queries...")
print_break()

all_trainers = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
all_emails = cursor.execute("SELECT * from customer_emails").fetchall()
individual_totals = cursor.execute("""
    SELECT implementation_specialists.first_name, implementation_specialists.last_name, COUNT(customer_emails.trainer_id) 
    FROM implementation_specialists 
    LEFT JOIN customer_emails 
    ON implementation_specialists.trainer_id = customer_emails.trainer_id 
    GROUP BY implementation_specialists.last_name 
    ORDER BY COUNT(customer_emails.trainer_id) DESC""").fetchall()
tas_total = cursor.execute("""
    SELECT COUNT(*)
    FROM customer_emails
    WHERE type = 'TAS'
""").fetchall()
hospital_total = cursor.execute("""
    SELECT COUNT(*)
    FROM customer_emails
    WHERE type = 'Hospital'
""").fetchall()

emails_november_2022 = cursor.execute("""
    SELECT *
    FROM customer_emails
    WHERE datetime_received > 202211010000 AND datetime_received < 202212010000
""").fetchall()

emails_december_2022 = cursor.execute("""
    SELECT *
    FROM customer_emails
    WHERE datetime_received > 202212010000 AND datetime_received < 202301010000
""").fetchall()

emails_january_2023 = cursor.execute("""
    SELECT *
    FROM customer_emails
    WHERE datetime_received > 202301010000 AND datetime_received < 202302010000
""").fetchall()

print(" - 5 total queries")

print_break()
print("Closing database connection...")
print_break()

connection.commit()
connection.close()

print_break()
print("Generating reports...")
print_break()

email_total = len(all_emails)
print(f" - Email Total: {email_total}")
print(f"    - November 2022 Email Total: {len(emails_november_2022)}")
print(f"    - December 2022 Email Total: {len(emails_december_2022)}")
print(f"    - January 2023 Email Total: {len(emails_january_2023)}")


print(f" - TAS: {tas_total[0][0]} ({math.floor((tas_total[0][0]/email_total)*100)}%)")
print(f" - Hospital: {hospital_total[0][0]} ({math.floor((hospital_total[0][0]/email_total)*100)}%)")

print(" - Implementation Specialists: Total Emails Assigned")
for trainer in individual_totals:
    print(f'    - {trainer[0]} {trainer[1]}: {trainer[2]}')


print("...SCRIPT END")
print("=========================")