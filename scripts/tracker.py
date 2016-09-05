#!/usd/bin/env python3
import csv
import datetime
from progress.bar import Bar

# Imports a CSV sheet and returns a list of dictionnaries
def csvToList(path):
    reader = csv.DictReader(open(path))
    result = []
    for dict in reader:
        result.append(dict)
    return result

# Searches through the accounts and return and attribute for the given account
def attributeFind(account, attribute):
    # Investigate list indexing and list length...
    for i in range(0,(len(accounts_raw))):
        current_account = accounts_raw[i]
        if current_account['account_number'] == account:
            return current_account[attribute]

# Converts an Angaza time to a datetime format
def toTime(angaza_time):
    return datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S')

# Converts an Angaza time with ms to a datetime format
def toTime_ms(angaza_time):
    return datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S.%f')

# Returns 1 if date is of today's month, 0 otherwise
def thisMonth(date, today):
    if date.year == today.year and date.month==today.month:
        return 1
    else:
        return 0

# Returns a datetime.timedelta in weeks
def deltaToWeeks(timedelta):
    result = timedelta.days/7
    result += timedelta.seconds/7/(3600*24)
    result += timedelta.microseconds/7/(3600*24)/1000000
    return result

# Returns the expected payment
def expect_payment(start,end,activated,plan):
    # Defining the plan duration as a timedelta object
    duration = datetime.timedelta((len(plan)-1) * 7,0,0)
    # Defining unlocked date as activated + duration
    unlocked = activated + duration
    # Case where the observation period is outside the plan
    if activated > end or unlocked < start:
        return 0
    # Case where the observation period includes the full plan
    elif activated >= start and unlocked <= end:
        return plan[len(plan)-1]
    # Case where the plan doesnt finish in the observation period
    elif unlocked > end and activated >= start:
        return plan[int(deltaToWeeks(end - activated))]
    # Case where the plan doesn't start in the observation period
    elif activated < start and unlocked <= end:
        return plan[len(plan)-1] - plan[len(plan) - int(deltaToWeeks(unlocked-start)) - 1]
    # Case where the observation period is included within the plan
    else:
        return plan[len(plan) - int(deltaToWeeks(unlocked-end)) - 2] - plan[int(deltaToWeeks(start-activated))]

# Locale variable for payment plans
plans = {}
plans['Eco-18-Pilot'] = [10000]
for i in range(1,19):
    plans['Eco-18-Pilot'].append(i*5000+10000)
plans['Eco-0-Pilot'] = [80000]

# Locale variables for solar points
points = {}
# Definition for Eco-18-Pilot plan (1 at the end)
points['Eco-18-Pilot'] = []
for i in range(0,18):
    points['Eco-18-Pilot'].append(0)
points['Eco-18-Pilot'].append(1)
# Definition for Eco-0-Pilot plan (1 upfront)
points['Eco-0-Pilot'] = [1]

# Imports raw accounts and payments files
accounts_raw = csvToList('accounts.csv')
payments_raw = csvToList('payments.csv')

# Defining the report's dates
print(chr(27))
print('############################################')
print('####### EASY SOLAR REPORTING TOOL V0 #######')
print('############################################')
print(chr(27))
question = input('Do you want to use TODAY as the end date for this reporting database? (y/n) ')
if question == 'y':
    report_end = datetime.datetime.today()
else:
    year = input(' Year? ')
    month = input(' Month? ')
    day = input(' Day? ')
    report_end = datetime.datetime(int(year),int(month),int(day),23,59,59,999999)
print(chr(27))

report_start = datetime.datetime(2016,3,1,00,00,00,000000)
today = datetime.datetime.today()

# Generating the progress bar
bar = Bar('Generating Database', max=len(payments_raw))

# Creates the target dictionnary
data = {}
# Investigate list indexing and list length...
for i in range(0,(len(payments_raw))):
    bar.next()
    # Defines the current payment for ease of coding
    pay = payments_raw[i]
    # Checking that the payment is whithing the report's range
    if toTime(pay['recorded_utc']) >= start_date and toTime(pay['recorded_utc']) <= end_date:
        # Checking whether it's a new account
        if pay['account'] in data.keys():
            # Updating the existing account in the database
            # Defines the current account for ease of coding
            line = data[pay['account']]
            # Updating before last payment information from database
            line['lastlastPay_date'] = line['lastPay_date']
            line['lastlastPay_amount'] = line['lastPay_amount']
            # Updating last payment information
            line['lastPay_date'] = toTime(pay['recorded_utc'])
            line['lastPay_amount'] = int(pay['amount'])
            line['total_paid'] = int(pay['new_total_paid'])
            line['pay_number'] += 1
            line['pay_thisMonth'] += thisMonth(line['lastPay_date'],report_end)*int(line['lastPay_amount'])
            # Complex calculations here (number of times disabeld etc.)
        else:
            # Creating the account in the database
            account = pay['account']
            # Deleting useless keys in the dictionnary
            del pay['account']
            del pay['organization']
            del pay['angaza_id']
            del pay['reversal']
            del pay['provider_transaction']
            del pay['synced']
            del pay['applied_utc'] # only keeping recorded date
            # Converting and renaming keys in the dictionnary
            pay['lastPay_amount'] = int(pay.pop('amount'))
            pay['lastPay_date']=toTime(pay.pop('recorded_utc'))
            pay['total_paid']=int(pay.pop('new_total_paid'))
            pay['account_angaza']=pay.pop('account_angaza_id')
            # Adding the new dictionnary to the database
            data[account] = pay
            line = data[account]
            # Create the additional keys needed here
            line['pay_number'] = 1
            line['reg_date']=attributeFind(account, 'registration_date_utc')
            line['reg_date']=toTime_ms(line['reg_date'])
            line['reg_agent']=attributeFind(account, 'registering_user')
            line['product']=attributeFind(account, 'attached_unit_type')
            line['lastlastPay_date']=''
            line['lastlastPay_amount']=0
            line['pay_thisMonth']=thisMonth(line['lastPay_date'],report_end)*line['lastPay_amount']
            # Total expected payments
            line['total_paid_expected']=expect_payment(report_start,report_end,line['reg_date'],plans[line['group_name']])
            # Defining the date for the beginning of the month
            month_start = datetime.datetime(report_end.year,report_end.month,1,00,00,00,000000)
            # Total payments expected this month
            line['pay_expected_thisMonth']=expect_payment(month_start,report_end,line['reg_date'],plans[line['group_name']])
            line['sPoints']=expect_payment(report_start,report_end,line['reg_date'],points[line['group_name']])
            line['sPoints_thisMonth']=expect_payment(month_start,report_end,line['reg_date'],points[line['group_name']])
            # Left to define
            line['disable_number']=0
            line['disable_days']=0
            line['disable_days_over1']=0
            line['pay_number_expected']=0

bar.finish()

for account in data:
    date_diff = datetime.datetime.today()-data[account]['reg_date']
    hours_diff = (date_diff.days + (date_diff.seconds)/3600)*24
    # print(hours_diff * float(data[account]['hour_price']))
    #print(account)
    #print('expected ' + str(data[account]['sPoints']))
    # print('this month ' + str(data[account]['sPoints_thisMonth']))

print(chr(27))
report = True
while report:
    choice = input('Do you want to filter on agent? (y/n) ')
    if choice == 'y':
        agent = input('Agent name... ')
    # Add proper agent filtering
    print(chr(27))
    print('****** NEW REPORT ******')
    print(' Period ranging from ' + str(start_date) + ' to ' + str(today))
    pay_collected = 0
    pay_expected = 0
    pay_number = 0
    pay_thisMonth = 0
    for account in data:
        pay_collected += data[account]['total_paid']

    print(chr(27))
    choice = input('Do you want to produce another report? (y/n) ')
    if choice == 'n':
        report = False
    for account in data:
        print(data[account])
