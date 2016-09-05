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
plans['Eco-18-Pilot'] = [10]
for i in range(1,19):
    plans['Eco-18-Pilot'].append(i*5+10)
plans['Eco-0-Pilot'] = [80]

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
print(chr(27) + "[2J")
question = input('Do you want to use today as the end date? (y/n) ')
if question == 'y':
    today = datetime.datetime.today()
else:
    year = input(' Year? ')
    month = input(' Month? ')
    day = input(' Day? ')
    today = datetime.datetime(int(year),int(month),int(day),23,59,59,999999)
print(chr(27))

start_date = datetime.datetime(2016,3,1,00,00,00,000000)

bar = Bar('Generating Database', max=len(payments_raw))

# Creates the target dictionnary
data = {}
# Investigate list indexing and list length...
for i in range(0,(len(payments_raw))):
    bar.next()
    # Defines the current payment for ease of coding
    pay = payments_raw[i]
    # Checks whether it's a new account
    if pay['account'] in data.keys():
        # Updating the existing account in the database
        # Defines the current account for ease of coding
        line = data[pay['account']]
        # Updating before last payment information from database
        line['lastPay_date']=line['recorded_date']
        line['lastPay_amount']=line['amount']
        # Updating last payment information
        line['recorded_date']=toTime(pay['recorded_utc'])
        line['applied_date']=toTime(pay['applied_utc'])
        line['new_total_paid']=pay['new_total_paid']
        line['pay_number'] += 1
        line['pay_thisMonth'] += thisMonth(line['recorded_date'],today)*int(pay['amount'])
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
        # Converting keys in the dictionnary
        pay['amount']=int(pay['amount'])
        pay['new_total_paid']=int(pay['new_total_paid'])
        # Renaming keys in the dictionnary
        pay['account_angaza']=pay.pop('account_angaza_id')
        pay['recorded_date']=toTime(pay.pop('recorded_utc'))
        pay['applied_date']=toTime(pay.pop('applied_utc'))
        pay['total_paid']=pay.pop('new_total_paid')
        # Adding the new dictionnary to the database
        data[account] = pay
        line = data[account]
        # Create the additional keys needed here
        line['pay_number'] = 1
        line['reg_date']=attributeFind(account, 'registration_date_utc')
        line['reg_date']=toTime_ms(line['reg_date'])
        line['reg_agent']=attributeFind(account, 'registering_user')
        # line['unlock_price']=int(attributeFind(account, 'unlock_price'))
        # line['upfront_price']=int(attributeFind(account, 'upfront_price'))
        line['product']=attributeFind(account, 'attached_unit_type')
        # line['hour_price']=float(attributeFind(account, 'hour_price'))
        line['lastPay_date']=''
        line['lastPay_amount']=0
        line['pay_thisMonth']=thisMonth(line['recorded_date'],today)*line['amount']
        # Total expected payments
        line['pay_expected']=expect_payment(line['reg_date'],today,line['reg_date'],plans[line['group_name']])
        # Total expected solar points
        line['sPoints']=expect_payment(line['reg_date'],today,line['reg_date'],points[line['group_name']])
        # Defining the date for the beginning of the month
        month_start = datetime.datetime(today.year,today.month,1,00,00,00,000000)
        # Total payments expected this month
        line['pay_expected_thisMonth']=expect_payment(month_start,today,line['reg_date'],plans[line['group_name']])
        # Total solar points expected this month
        line['sPoints_thisMonth']=expect_payment(month_start,today,line['reg_date'],points[line['group_name']])
        # Left to define
        line['disable_number']=0
        line['disable_days']=0
        line['disable_days_over1']=0

bar.finish()

for account in data:
    date_diff = datetime.datetime.today()-data[account]['reg_date']
    hours_diff = (date_diff.days + (date_diff.seconds)/3600)*24
    # print(hours_diff * float(data[account]['hour_price']))
    #print(account)
    #print('expected ' + str(data[account]['sPoints']))
    # print('this month ' + str(data[account]['sPoints_thisMonth']))
