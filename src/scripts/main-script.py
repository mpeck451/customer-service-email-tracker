import csv
import sqlite3

print("Script Start...")
csv_data = []

print("Connecting to sqlite3 database...")

print("Opening csv file...")
with open('../../../database/customer-emails.csv') as customer_emails:
    file_reader = csv.DictReader(customer_emails)
    csv_data = list(file_reader)
for row in csv_data:
    print(row)
master_fields = list(csv_data[0].keys())
print("Updating database tables...")

print("Closing database connection...")

print("Generating reports...")

print("...Script End")