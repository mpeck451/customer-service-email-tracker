import datetime
import csv

def normalize_datetime(datetime_int):
    datetime_str = str(datetime_int)
    python_datetime = datetime.datetime(int(datetime_str[:4]), int(datetime_str[4:6]), int(datetime_str[6:8]), hour = int(datetime_str[8:10]), minute = int(datetime_str[10:12]))
    return python_datetime

def generate_report(email_array):
    report_data = {
        'email_total': len(email_array),
        'intervals': {
            'same_day_assignments': {
                'number': 0,
                'percentage': ''
            },
            'under_24_hours': {
                'number': 0,
                'percentage': ''
            },
            'between_24_and_48': {
                'number': 0,
                'percentage': ''
            },
            'between_48_and_72': {
                'number': 0,
                'percentage': ''
            },
            'greater_than_72': {
                'number': 0,
                'percentage': ''
            },
        },
        'benchmarks': {
            'within_24_hours': {
                'number': 0,
                'percentage': ''
            }, 
            'within_48_hours': {
                'number': 0,
                'percentage': ''
            },
            'within_72_hours': {
                'number': 0,
                'percentage': ''
            },
        },
        'weekday_breakdown': {
            'sunday_emails': {
                'number': 0,
                'percentage': ''
            },
            'monday_emails': {
                'number': 0,
                'percentage': ''
            },
            'tuesday_emails': {
                'number': 0,
                'percentage': ''
            },
            'wednesday_emails': {
                'number': 0,
                'percentage': ''
            },
            'thursday_emails': {
                'number': 0,
                'percentage': ''
            },
            'friday_emails': {
                'number': 0,
                'percentage': ''
            },
            'saturday_emails': {
                'number': 0,
                'percentage': ''
            },
        },
        'markets': {
            'tas': {
                'number': 0,
                'percentage': ''
            },
            'hospital': {
                'number': 0,
                'percentage': ''
            }
        }
    }

    def calculate_percentage(numerator, denominator = report_data['email_total']):
        return f"({round(((numerator/denominator)*100), 1)}%)"


    for email in email_array:
        email_id = email[0]
        market_type = email[7]
        datetime_received = normalize_datetime(email[1])
        datetime_assigned = normalize_datetime(email[2])
        datetime_delta = datetime_assigned - datetime_received

        if (datetime_received.strftime('%y-%m-%d') == datetime_assigned.strftime('%y-%m-%d')):
            report_data['intervals']['same_day_assignments']['number'] += 1

        #Subtracts 2 days from emails receieved on a Friday, but not assigned on Friday. Does not account for sat, sun email assignments.
        if (datetime_received.strftime('%a') == "Fri" and datetime_assigned.strftime('%a') != 'Fri'):
            datetime_delta -= datetime.timedelta(days = 2)
        #Subtracts 1 day from emails received on a Saturday, but not assigned on Saturday
        if (datetime_received.strftime('%a') == "Sat" and datetime_assigned.strftime('%a') != 'Sat'):
            datetime_delta -= datetime.timedelta(days = 1)
        if '-' in str(datetime_delta):
            print(f"""Calcuation Error: 
            {email}
            {datetime_delta}""")


        if (not ('day' in str(datetime_delta))):
            report_data['intervals']['under_24_hours']['number'] += 1
        if ('1 day' in str(datetime_delta)):
            report_data['intervals']['between_24_and_48']['number'] += 1
        if ('2 days' in str(datetime_delta)):
            report_data['intervals']['between_48_and_72']['number'] += 1
        report_data['intervals']['greater_than_72']['number'] = report_data['email_total'] - report_data['intervals']['under_24_hours']['number'] - report_data['intervals']['between_24_and_48']['number'] - report_data['intervals']['between_48_and_72']['number']
       
        match datetime_received.strftime('%a'):
            case 'Sun':
                report_data['weekday_breakdown']['sunday_emails']['number'] += 1
            case 'Mon':
                report_data['weekday_breakdown']['monday_emails']['number'] += 1
            case 'Tue':
                report_data['weekday_breakdown']['tuesday_emails']['number'] += 1
            case 'Wed':
                report_data['weekday_breakdown']['wednesday_emails']['number'] += 1
            case 'Thu':
                report_data['weekday_breakdown']['thursday_emails']['number'] += 1
            case 'Fri':
                report_data['weekday_breakdown']['friday_emails']['number'] += 1
            case 'Sat':
                report_data['weekday_breakdown']['saturday_emails']['number'] += 1

        match market_type:
            case 'TAS':
                report_data['markets']['tas']['number'] += 1
            case 'Hospital':
                report_data['markets']['hospital']['number'] += 1
            case _:
                print(f"Error: Market Type not recognized ({market_type}) in email ID: {email_id}")

    #Add Same Day Assignment percentage data
    report_data['intervals']['same_day_assignments']['percentage'] = calculate_percentage(report_data['intervals']['same_day_assignments']['number'])

    #Add market percentage data
    report_data['markets']['tas']['percentage'] = calculate_percentage(report_data['markets']['tas']['number'])
    report_data['markets']['hospital']['percentage'] = calculate_percentage(report_data['markets']['hospital']['number'])

    #Add Weekday percentage data
    report_data['weekday_breakdown']['sunday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['sunday_emails']['number'])
    report_data['weekday_breakdown']['monday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['monday_emails']['number'])
    report_data['weekday_breakdown']['tuesday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['tuesday_emails']['number'])
    report_data['weekday_breakdown']['wednesday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['wednesday_emails']['number'])
    report_data['weekday_breakdown']['thursday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['thursday_emails']['number'])
    report_data['weekday_breakdown']['friday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['friday_emails']['number'])
    report_data['weekday_breakdown']['saturday_emails']['percentage'] = calculate_percentage(report_data['weekday_breakdown']['saturday_emails']['number'])
    
    #Add interval percentage data
    report_data['intervals']['under_24_hours']['percentage'] = calculate_percentage(report_data['intervals']['under_24_hours']['number'])
    report_data['intervals']['between_24_and_48']['percentage'] = calculate_percentage(report_data['intervals']['between_24_and_48']['number'])
    report_data['intervals']['between_48_and_72']['percentage'] = calculate_percentage(report_data['intervals']['between_48_and_72']['number'])
    report_data['intervals']['greater_than_72']['percentage'] = calculate_percentage(report_data['intervals']['greater_than_72']['number'])

    #Add benchmark data            
    report_data['benchmarks']['within_24_hours']['number'] = report_data['intervals']['under_24_hours']['number']
    report_data['benchmarks']['within_24_hours']['percentage'] = calculate_percentage(report_data['benchmarks']['within_24_hours']['number'])
    report_data['benchmarks']['within_48_hours']['number'] = report_data['intervals']['under_24_hours']['number'] + report_data['intervals']['between_24_and_48']['number']
    report_data['benchmarks']['within_48_hours']['percentage'] = calculate_percentage(report_data['benchmarks']['within_48_hours']['number'])
    report_data['benchmarks']['within_72_hours']['number'] = report_data['intervals']['under_24_hours']['number'] + report_data['intervals']['between_24_and_48']['number'] + report_data['intervals']['between_48_and_72']['number']
    report_data['benchmarks']['within_72_hours']['percentage'] = calculate_percentage(report_data['benchmarks']['within_72_hours']['number'])
    return report_data

def generate_monthly_reports(data):
    report_object = {
        'available_months': [],
        'emails_by_month': [],
    }
    for email in data:
        datetime_received = normalize_datetime(email[1])
        month_year = datetime_received.strftime("%y-%m-%b")
        if (not(month_year in report_object['available_months'])):
            report_object['available_months'].append(month_year)
    for month in report_object['available_months']:
        report_object['emails_by_month'].append([])
    for email in data:
        datetime_received = normalize_datetime(email[1])
        month_year = datetime_received.strftime("%y-%m-%b")
        month_year_index = report_object['available_months'].index(month_year)
        report_object['emails_by_month'][month_year_index].append(email)
    for month in report_object['emails_by_month']:
        month_report = generate_report(month)
    return report_object

def write_report(data, file_name):
    report_data = generate_report(data)
    with open (f"../../../reports/{file_name}.txt", 'w') as report:
        report.writelines(f"{file_name}\n")
        report.writelines(f" - Email Total: {len(data)}")
        report.writelines(f" - Stats:\n")
        report.writelines(f"    - Assignments by Intervals (Weekend Time Ignored)\n")
        report.writelines(f"    =================================================\n")
        report.writelines(f"       - Same Day Assignments:                {report_data['intervals']['same_day_assignments']['number']} {report_data['intervals']['same_day_assignments']['percentage']}\n")
        report.writelines(f"       - Assignments between 0 and 24-hours:  {report_data['intervals']['under_24_hours']['number']} {report_data['intervals']['under_24_hours']['percentage']}\n")
        report.writelines(f"       - Assignments between 24 and 48 hours: {report_data['intervals']['between_24_and_48']['number']} {report_data['intervals']['between_24_and_48']['percentage']}\n")
        report.writelines(f"       - Assignments between 48 and 72 hours: {report_data['intervals']['between_48_and_72']['number']} {report_data['intervals']['between_48_and_72']['percentage']}\n")
        report.writelines(f"       - Assignments greater than 72 hours:   {report_data['intervals']['greater_than_72']['number']} {report_data['intervals']['greater_than_72']['percentage']}\n")
        report.writelines(f"    =================================================\n")
        report.writelines(f"    - Assignments by Benchmarks (Weekend Time Ignored)\n")
        report.writelines(f"    ==================================================\n")
        report.writelines(f"       - Assignments within 24-hours: {report_data['benchmarks']['within_24_hours']['number']} {report_data['benchmarks']['within_24_hours']['percentage']}\n")
        report.writelines(f"       - Assignments within 48 hours: {report_data['benchmarks']['within_48_hours']['number']} {report_data['benchmarks']['within_48_hours']['percentage']}\n")
        report.writelines(f"       - Assignments within 72 hours: {report_data['benchmarks']['within_72_hours']['number']} {report_data['benchmarks']['within_72_hours']['percentage']}\n")
        report.writelines(f"    ==================================================\n")
        report.writelines(f"    - Weekday Breakdown\n")
        report.writelines(f"    ===================\n")
        report.writelines(f"       - Sunday:    {report_data['weekday_breakdown']['sunday_emails']['number']} {report_data['weekday_breakdown']['sunday_emails']['percentage']}\n")
        report.writelines(f"       - Monday:    {report_data['weekday_breakdown']['monday_emails']['number']} {report_data['weekday_breakdown']['monday_emails']['percentage']}\n")
        report.writelines(f"       - Tuesday:   {report_data['weekday_breakdown']['tuesday_emails']['number']} {report_data['weekday_breakdown']['tuesday_emails']['percentage']}\n")
        report.writelines(f"       - Wednesday: {report_data['weekday_breakdown']['wednesday_emails']['number']} {report_data['weekday_breakdown']['wednesday_emails']['percentage']}\n")
        report.writelines(f"       - Thursday:  {report_data['weekday_breakdown']['thursday_emails']['number']} {report_data['weekday_breakdown']['thursday_emails']['percentage']}\n")
        report.writelines(f"       - Friday:    {report_data['weekday_breakdown']['friday_emails']['number']} {report_data['weekday_breakdown']['friday_emails']['percentage']}\n")
        report.writelines(f"       - Saturday:  {report_data['weekday_breakdown']['saturday_emails']['number']} {report_data['weekday_breakdown']['saturday_emails']['percentage']}\n")
        report.writelines(f"    ===================\n")
        report.writelines(f"    - Market Breakdown\n")
        report.writelines(f"    ==================\n")
        report.writelines(f"       - TAS:      {report_data['markets']['tas']['number']} {report_data['markets']['tas']['percentage']}\n")
        report.writelines(f"       - Hospital: {report_data['markets']['hospital']['number']} {report_data['markets']['hospital']['percentage']}\n")
        report.writelines(f"    ==================\n")
        report.writelines("\nEmails:\n")
        for email in data:
            report.writelines(f"{email}\n")
    
