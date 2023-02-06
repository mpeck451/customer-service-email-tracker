import csv
import sys
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

try:
    should_write_txt = bool(sys.argv[1])
    if should_write_txt:
        print("Txt files will be generated.")
    else:
        print("Txt files will not be generated")
except:
    should_write_txt = False
    print("No argument passed. Txt files will not be generated.")

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
#cursor.execute("""CREATE TABLE implementation_specialists (
#    trainer_id INTEGER,
#    first_name TEXT,
#    last_name TEXT,
#    position TEXT,
#    team INTEGER,
#    is_incumbent BOOLEAN)""")
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
old_implementation_table = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
old_email_table = cursor.execute("SELECT * from customer_emails").fetchall()
new_trainers = len(csv_department_data) - len(old_implementation_table)
new_emails = len(csv_email_data) - len(old_email_table)
print(f" - {new_trainers} new trainers.")
print(f" - {new_emails} new emails.")

print_section("Updating database tables...")
if (new_emails > 0):
    print(f" - {new_emails} added to customer_emails table.")
    new_email_data = csv_email_data[-(new_emails):]
    for email in new_email_data:
        print(f" - {email}")        
    cursor.executemany("INSERT INTO customer_emails VALUES (?, ?, ?, ?, ?, ?, ?, ?)", new_email_data)
else:
    print(" - No new entries for customer_emails table.")
if (new_trainers > 0):
    print(f" - {new_trainers} added to implementation_specialists table.")
    new_trainers = csv_department_data[-(new_trainers):]
    cursor.executemany("INSERT INTO implementation_specialists VALUES (?, ?, ?, ?, ?, ?)", new_trainers)
else:
    print(" - No new entries for implementation_specialists table.")

for trainer in csv_department_data:
    cursor.execute(f"""
        UPDATE implementation_specialists
        SET
            trainer_id = {int(trainer[0])},
            first_name = "{str(trainer[1])}",
            last_name = "{str(trainer[2])}",
            position = "{str(trainer[3])}",
            team = {int(trainer[4])},
            is_incumbent = {int(trainer[5])}
        WHERE trainer_id = {int(trainer[0])};
    """)

for email in csv_email_data:
    cursor.execute(f"""
        UPDATE customer_emails
        SET email_id = {int(email[0])},
            datetime_received = {int(email[1])},
            datetime_assigned = {int(email[2])},
            trainer_id = {int(email[3])},
            sender_name = '{str(email[4])}',
            company = "{str(email[5])}",
            customer_id = {int(email[6])},
            type = '{str(email[7])}'
        WHERE email_id = {int(email[0])};
    """)
    
print_section("Executing additional queries...")
all_trainers = cursor.execute("SELECT * FROM implementation_specialists").fetchall()
#Don't change all_emails query. Especially the ORDER BY. Referenced in 'generate_monthly_report'. 
all_emails = cursor.execute("SELECT * from customer_emails ORDER BY datetime_received ASC").fetchall()
individual_totals = cursor.execute("""
    SELECT implementation_specialists.first_name, implementation_specialists.last_name, COUNT(customer_emails.trainer_id), implementation_specialists.is_incumbent
    FROM implementation_specialists
    LEFT JOIN customer_emails
    ON implementation_specialists.trainer_id = customer_emails.trainer_id
    GROUP BY implementation_specialists.last_name
    ORDER BY COUNT(customer_emails.trainer_id) DESC""").fetchall()
top_ten_common_customers = cursor.execute("""
    SELECT customer_id, company, COUNT(customer_id) 
    FROM customer_emails 
    GROUP BY customer_id 
    ORDER BY COUNT(customer_id) DESC
    LIMIT 10
""").fetchall()
print(" - 4 total queries")

print_section("Closing database connection...")
connection.commit()
connection.close()

print_section("Generating reports...")
all_emails_report = reports.generate_report(all_emails)
monthly_reports = reports.generate_monthly_reports(all_emails)
print(f" - Email Total: {all_emails_report['email_total']}")
if should_write_txt:
    reports.write_report(all_emails, 'all-emails')
for month in monthly_reports['available_months']:
    month_year_index = monthly_reports['available_months'].index(month)
    if should_write_txt:
        reports.write_report(monthly_reports['emails_by_month'][month_year_index], str(month))
    print(f"    - {month} Email Total: {len(monthly_reports['emails_by_month'][month_year_index])}")
print(f""" - Stats:
    - Assignments by Intervals (Weekend Time Ignored)
    =================================================
       - Same Day Assignments:                {all_emails_report['intervals']['same_day_assignments']['number']} {all_emails_report['intervals']['same_day_assignments']['percentage']}
       - Assignments between 0 and 24-hours:  {all_emails_report['intervals']['under_24_hours']['number']} {all_emails_report['intervals']['under_24_hours']['percentage']}
       - Assignments between 24 and 48 hours: {all_emails_report['intervals']['between_24_and_48']['number']} {all_emails_report['intervals']['between_24_and_48']['percentage']}
       - Assignments between 48 and 72 hours: {all_emails_report['intervals']['between_48_and_72']['number']} {all_emails_report['intervals']['between_48_and_72']['percentage']}
       - Assignments greater than 72 hours:   {all_emails_report['intervals']['greater_than_72']['number']} {all_emails_report['intervals']['greater_than_72']['percentage']}
    =================================================
    - Assignments by Benchmarks (Weekend Time Ignored)
    ==================================================
       - Assignments within 24-hours: {all_emails_report['benchmarks']['within_24_hours']['number']} {all_emails_report['benchmarks']['within_24_hours']['percentage']}
       - Assignments within 48 hours: {all_emails_report['benchmarks']['within_48_hours']['number']} {all_emails_report['benchmarks']['within_48_hours']['percentage']}
       - Assignments within 72 hours: {all_emails_report['benchmarks']['within_72_hours']['number']} {all_emails_report['benchmarks']['within_72_hours']['percentage']}
    ==================================================
    - Weekday Breakdown
    ===================
       - Sunday:    {all_emails_report['weekday_breakdown']['sunday_emails']['number']} {all_emails_report['weekday_breakdown']['sunday_emails']['percentage']}
       - Monday:    {all_emails_report['weekday_breakdown']['monday_emails']['number']} {all_emails_report['weekday_breakdown']['monday_emails']['percentage']}
       - Tuesday:   {all_emails_report['weekday_breakdown']['tuesday_emails']['number']} {all_emails_report['weekday_breakdown']['tuesday_emails']['percentage']}
       - Wednesday: {all_emails_report['weekday_breakdown']['wednesday_emails']['number']} {all_emails_report['weekday_breakdown']['wednesday_emails']['percentage']}
       - Thursday:  {all_emails_report['weekday_breakdown']['thursday_emails']['number']} {all_emails_report['weekday_breakdown']['thursday_emails']['percentage']}
       - Friday:    {all_emails_report['weekday_breakdown']['friday_emails']['number']} {all_emails_report['weekday_breakdown']['friday_emails']['percentage']}
       - Saturday:  {all_emails_report['weekday_breakdown']['saturday_emails']['number']} {all_emails_report['weekday_breakdown']['saturday_emails']['percentage']}
    ===================
    - Market Breakdown
    ==================
       - TAS:      {all_emails_report['markets']['tas']['number']} {all_emails_report['markets']['tas']['percentage']}
       - Hospital: {all_emails_report['markets']['hospital']['number']} {all_emails_report['markets']['hospital']['percentage']}
    ==================""")

print(" - Department Data")
print("    ===============================================")
implementation_titles = {}
for trainer in all_trainers:
    if len(trainer[3]) > 0 and not trainer[3] in implementation_titles:
        implementation_titles[trainer[3]] = 0
    if trainer[3] in implementation_titles:
        implementation_titles[trainer[3]] += 1
for title in implementation_titles:
    print(f"    - {title}: {implementation_titles[title]}")
print("    ===============================================")

print(""" - Total Emails Assigned by Individual Since 11/1/2022
    ===============================================""")
trainer_rank = 0
for trainer in individual_totals:
    trainer_rank += 1
    if (trainer[3]):
        print(f"    {trainer_rank}. {trainer[0]} {trainer[1]}: {trainer[2]}")
print(f"    ===============================================")
print(f"    - Former Implementaion Specialists")
for trainer in individual_totals:
    if (not trainer[3]):
        print(f"       - {trainer[0]} {trainer[1]}: {trainer[2]}")
print(f"    ===============================================")
print(" - Most Frequent Customers Since 11/1/2022")
print(f"    =====================")
for customer in top_ten_common_customers:
    print(f"    - {customer[0]} {customer[1]}: {customer[2]}")
print(f"    =====================")

print("...SCRIPT END")
print("=========================")