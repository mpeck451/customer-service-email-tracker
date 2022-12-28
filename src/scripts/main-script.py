import csv
import sqlite3

print("Script Start...")
csv_email_data = []
csv_department_data = []

print("Opening csv files...")
with open('../../../database/implementation-department.csv') as department_data:
    file_reader = csv.DictReader(department_data)
    csv_department_data = list(file_reader)
for row in csv_department_data:
    print(row)
with open('../../../database/customer-emails.csv') as customer_emails:
    file_reader = csv.DictReader(customer_emails)
    csv_email_data = list(file_reader)
for row in csv_email_data:
    print(row)
master_fields = list(csv_email_data[0].keys())
print(master_fields)

print("Connecting to sqlite3 database...")

print("Updating database tables...")

print("Closing database connection...")

print("Generating reports...")

print("...Script End")