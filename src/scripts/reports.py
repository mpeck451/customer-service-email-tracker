import datetime

def calculate_percentage(numerator, denominator):
    return f"({round(((numerator/denominator)*100), 1)}%)"

def generate_report(email_array):
    report_data = {
        'email_total': len(email_array),
        'intervals': {
            'under_24_hours': 0,
            'between_24_and_48': 0,
            'between_48_and_72': 0,
            'greater_than_72': 0,
            'percentages': {}
        },
        'benchmarks': {
            'percentages': {}
        },
        'weekday_breakdown': {
            'sunday_emails': 0,
            'monday_emails': 0,
            'tuesday_emails': 0,
            'wednesday_emails': 0,
            'thursday_emails': 0,
            'friday_emails': 0,
            'saturday_emails': 0,
        },
    }

    def calculate_percentage(numerator, denominator = report_data['email_total']):
        return f"({round(((numerator/denominator)*100), 1)}%)"


    for email in email_array:
        #email_id = email[0]
        datetime_received_string = str(email[1])
        datetime_assigned_string = str(email[2])
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
            report_data['intervals']['under_24_hours'] += 1
        if ('1 day' in str(datetime_delta)):
            report_data['intervals']['between_24_and_48'] += 1
        if ('2 days' in str(datetime_delta)):
            report_data['intervals']['between_48_and_72'] += 1
        report_data['intervals']['greater_than_72'] = report_data['email_total'] - report_data['intervals']['under_24_hours'] - report_data['intervals']['between_24_and_48'] - report_data['intervals']['between_48_and_72']
        match datetime_received.strftime('%a'):
            case 'Sun':
                report_data['weekday_breakdown']['sunday_emails'] += 1
            case 'Mon':
                report_data['weekday_breakdown']['monday_emails'] += 1
            case 'Tue':
                report_data['weekday_breakdown']['tuesday_emails'] += 1
            case 'Wed':
                report_data['weekday_breakdown']['wednesday_emails'] += 1
            case 'Thu':
                report_data['weekday_breakdown']['thursday_emails'] += 1
            case 'Fri':
                report_data['weekday_breakdown']['friday_emails'] += 1
            case 'Sat':
                report_data['weekday_breakdown']['saturday_emails'] += 1

    #Add interval percentage data
    report_data['intervals']['percentages']['under_24_hours'] = calculate_percentage(report_data['intervals']['under_24_hours'])
    report_data['intervals']['percentages']['between_24_and_48'] = calculate_percentage(report_data['intervals']['between_24_and_48'])
    report_data['intervals']['percentages']['between_48_and_72'] = calculate_percentage(report_data['intervals']['between_48_and_72'])
    report_data['intervals']['percentages']['greater_than_72'] = calculate_percentage(report_data['intervals']['greater_than_72'])

    #Add benchmark data            
    report_data['benchmarks']['within_24_hours'] = report_data['intervals']['under_24_hours']
    report_data['benchmarks']['percentages']['within_24_hours'] = calculate_percentage(report_data['benchmarks']['within_24_hours'])
    report_data['benchmarks']['within_48_hours'] = report_data['intervals']['under_24_hours'] + report_data['intervals']['between_24_and_48']
    report_data['benchmarks']['percentages']['within_48_hours'] = calculate_percentage(report_data['benchmarks']['within_48_hours'])
    report_data['benchmarks']['within_72_hours'] = report_data['intervals']['under_24_hours'] + report_data['intervals']['between_24_and_48'] + report_data['intervals']['between_48_and_72']
    report_data['benchmarks']['percentages']['within_72_hours'] = calculate_percentage(report_data['benchmarks']['within_72_hours'])
    return report_data