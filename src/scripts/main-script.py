import csv
import sqlite3
import datetime

print("=========================")
print("SCRIPT START...")
csv_email_data = []
csv_department_data = []

def print_section(string):
    print("-------------------------")
    print(string)
    print("-------------------------")

print_section("Connecting to sqlite3 database...")

connection = sqlite3.connect("../../../database/implementation.db")
cursor = connection.cursor()
print(f" - {connection}")
print(f" - {cursor}")

print_section("Opening csv files...")

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

print_section("Updating database tables...")
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

print_section("Executing additional queries...")

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
same_day_assignments = cursor.execute("""
    SELECT COUNT(*) 
    FROM customer_emails 
    WHERE FLOOR(datetime_received/10000) = FLOOR(datetime_assigned/10000)
""").fetchall()
top_ten_common_customers = cursor.execute("""
    SELECT customer_id, company, COUNT(customer_id) 
    FROM customer_emails 
    GROUP BY customer_id 
    ORDER BY COUNT(customer_id) DESC
    LIMIT 10
""").fetchall()

print(" - 10 total queries")

print_section("Closing database connection...")

connection.commit()
connection.close()

print_section("Generating reports...")
email_total = len(all_emails)

under_24_hours = 0
one_day = 0
two_days = 0
three_or_more_days = 0

sunday_emails = 0
monday_emails = 0
tuesday_emails = 0
wednesday_emails = 0
thursday_emails = 0
friday_emails = 0
saturday_emails = 0

for email in all_emails:
    email_id = email[0]
    datetime_received_string = str(email[1])
    datetime_assigned_string = str(email[2])
    date_received = datetime_received_string[:4] + "-" + datetime_received_string[4:6] + "-" + datetime_received_string[6:8]
    time_received = datetime_received_string[8:10] + ":" + datetime_received_string[10:12]
    date_assigned = datetime_assigned_string[:4] + "-" + datetime_assigned_string[4:6] + "-" + datetime_assigned_string[6:8]
    time_assigned = datetime_assigned_string[8:10] + ":" + datetime_assigned_string[10:12]
    datetime_received = datetime.datetime(int(datetime_received_string[:4]), int(datetime_received_string[4:6]), int(datetime_received_string[6:8]), hour = int(datetime_received_string[8:10]), minute = int(datetime_received_string[10:12]))
    datetime_assigned = datetime.datetime(int(datetime_assigned_string[:4]), int(datetime_assigned_string[4:6]), int(datetime_assigned_string[6:8]), hour = int(datetime_assigned_string[8:10]), minute = int(datetime_assigned_string[10:12]))
    
    datetime_delta = datetime_assigned - datetime_received

    #Subtracts 2 days from emails receieved on a Friday, but not assigned on Friday. Does not account for sat, sun email assignments.
    if (datetime_received.strftime('%a') == "Fri" and datetime_assigned.strftime('%a') != 'Fri'):
        datetime_delta -= datetime.timedelta(days = 2)
    
    #Subtracts 1 day from emails received on a Saturday, but not assigned on Saturday
    if (datetime_received.strftime('%a') == "Sat" and datetime_assigned.strftime('%a') != 'Sat'):
        print(datetime_delta - datetime.timedelta(days = 1))
        datetime_delta -= datetime.timedelta(days = 1)

    if '-' in str(datetime_delta):
        print(f"""Calcuation Error: 
        {email}
        {datetime_delta}""")

    if (not ('day' in str(datetime_delta))):
        under_24_hours += 1
    if ('1 day' in str(datetime_delta)):
        one_day += 1
    if ('2 days' in str(datetime_delta)):
        two_days += 1

    match datetime_received.strftime('%a'):
        case 'Sun':
            sunday_emails += 1
        case 'Mon':
            monday_emails += 1
        case 'Tue':
            tuesday_emails += 1
        case 'Wed':
            wednesday_emails += 1
        case 'Thu':
            thursday_emails += 1
        case 'Fri':
            friday_emails += 1
        case 'Sat':
            saturday_emails += 1

three_or_more_days = email_total - under_24_hours - one_day - two_days

def print_percentage(numerator, denominator = email_total):
    return f"({round(((numerator/denominator)*100), 1)}%)"
print(f" - Email Total: {email_total}")
print(f"    - November 2022 Email Total: {len(emails_november_2022)}")
print(f"    - December 2022 Email Total: {len(emails_december_2022)}")
print(f"    - January 2023 Email Total: {len(emails_january_2023)}")

print(f" - Stats:")
print(f"    - Same Day Assignments: {same_day_assignments[0][0]} {print_percentage(same_day_assignments[0][0])}")
print(f"    - Assignments by Intervals (Weekend Days Subtracted)")
print(f"       - Assignments Under 24-hours: {under_24_hours} {print_percentage(under_24_hours)}")
print(f"       - Assignments between 24 and 48 hours: {one_day} {print_percentage(one_day)}")
print(f"       - Assignments between 48 and 72 hours: {two_days} {print_percentage(two_days)}")
print(f"       - Assignments greater than 72 hours: {three_or_more_days} {print_percentage(three_or_more_days)}")
print(f"    - Weekday Breakdown")
print(f"       - Sunday: {sunday_emails}")
print(f"       - Monday: {monday_emails}")
print(f"       - Tuesday: {tuesday_emails}")
print(f"       - Wednesday:{wednesday_emails}")
print(f"       - Thursday: {thursday_emails}")
print(f"       - Friday: {friday_emails}")
print(f"       - Saturday: {saturday_emails}")
print(f"    - Market Breakdown")
print(f"       - TAS: {tas_total[0][0]} {print_percentage(tas_total[0][0])}")
print(f"       - Hospital: {hospital_total[0][0]} {print_percentage(hospital_total[0][0])}")

print(" - Implementation Specialists: Total Emails Assigned")
for trainer in individual_totals:
    print(f'    - {trainer[0]} {trainer[1]}: {trainer[2]}')

print(" - Most Frequent Customers")
for customer in top_ten_common_customers:
    print(f"    - {customer[0]} {customer[1]}: {customer[2]}")

print("...SCRIPT END")
print("=========================")