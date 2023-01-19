import csv
import sqlite3
import reports

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
old_implementation_table = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
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
top_ten_common_customers = cursor.execute("""
    SELECT customer_id, company, COUNT(customer_id) 
    FROM customer_emails 
    GROUP BY customer_id 
    ORDER BY COUNT(customer_id) DESC
    LIMIT 10
""").fetchall()
print(" - 7 total queries")

print_section("Closing database connection...")
connection.commit()
connection.close()

print_section("Generating reports...")
all_emails_report = reports.generate_report(all_emails)
print(f" - Email Total: {all_emails_report['email_total']}")
print(f"    - November 2022 Email Total: {len(emails_november_2022)}")
print(f"    - December 2022 Email Total: {len(emails_december_2022)}")
print(f"    - January 2023 Email Total: {len(emails_january_2023)}")
print(f" - Stats:")
print(f"    - Same Day Assignments: {all_emails_report['intervals']['same_day_assignments']['number']} {all_emails_report['intervals']['same_day_assignments']['percentage']}")
print(f"    - Assignments by Intervals (Weekend Time Ignored)")
print(f"       - Assignments Under 24-hours: {all_emails_report['intervals']['under_24_hours']['number']} {all_emails_report['intervals']['under_24_hours']['percentage']}")
print(f"       - Assignments between 24 and 48 hours: {all_emails_report['intervals']['between_24_and_48']['number']} {all_emails_report['intervals']['between_24_and_48']['percentage']}")
print(f"       - Assignments between 48 and 72 hours: {all_emails_report['intervals']['between_48_and_72']['number']} {all_emails_report['intervals']['between_48_and_72']['percentage']}")
print(f"       - Assignments greater than 72 hours: {all_emails_report['intervals']['greater_than_72']['number']} {all_emails_report['intervals']['greater_than_72']['percentage']}")
print(f"    - Assignments by Benchmarks (Weekend Time Ignored)")
print(f"       - Assignments within 24-hours: {all_emails_report['benchmarks']['within_24_hours']['number']} {all_emails_report['benchmarks']['within_24_hours']['percentage']}")
print(f"       - Assignments within 48 hours: {all_emails_report['benchmarks']['within_48_hours']['number']} {all_emails_report['benchmarks']['within_48_hours']['percentage']}")
print(f"       - Assignments within 72 hours: {all_emails_report['benchmarks']['within_72_hours']['number']} {all_emails_report['benchmarks']['within_72_hours']['percentage']}")
print(f"       - Assignments greater than 72 hours: {all_emails_report['intervals']['greater_than_72']['number']} {all_emails_report['intervals']['greater_than_72']['percentage']}")
print(f"    - Weekday Breakdown")
print(f"       - Sunday: {all_emails_report['weekday_breakdown']['sunday_emails']['number']} {all_emails_report['weekday_breakdown']['sunday_emails']['percentage']}")
print(f"       - Monday: {all_emails_report['weekday_breakdown']['monday_emails']['number']} {all_emails_report['weekday_breakdown']['monday_emails']['percentage']}")
print(f"       - Tuesday: {all_emails_report['weekday_breakdown']['tuesday_emails']['number']} {all_emails_report['weekday_breakdown']['tuesday_emails']['percentage']}")
print(f"       - Wednesday: {all_emails_report['weekday_breakdown']['wednesday_emails']['number']} {all_emails_report['weekday_breakdown']['wednesday_emails']['percentage']}")
print(f"       - Thursday: {all_emails_report['weekday_breakdown']['thursday_emails']['number']} {all_emails_report['weekday_breakdown']['thursday_emails']['percentage']}")
print(f"       - Friday: {all_emails_report['weekday_breakdown']['friday_emails']['number']} {all_emails_report['weekday_breakdown']['friday_emails']['percentage']}")
print(f"       - Saturday: {all_emails_report['weekday_breakdown']['saturday_emails']['number']} {all_emails_report['weekday_breakdown']['saturday_emails']['percentage']}")
print(f"    - Market Breakdown")
print(f"       - TAS: {all_emails_report['markets']['tas']['number']} {all_emails_report['markets']['tas']['percentage']}")
print(f"       - Hospital: {all_emails_report['markets']['hospital']['number']} {all_emails_report['markets']['hospital']['percentage']}")
print(" - Implementation Specialists: Total Emails Assigned")
for trainer in individual_totals:
    print(f"    - {trainer[0]} {trainer[1]}: {trainer[2]} {reports.calculate_percentage(trainer[2], all_emails_report['email_total'])}")
print(" - Most Frequent Customers")
for customer in top_ten_common_customers:
    print(f"    - {customer[0]} {customer[1]}: {customer[2]} {reports.calculate_percentage(customer[2], all_emails_report['email_total'])}")

print("...SCRIPT END")
print("=========================")