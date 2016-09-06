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
    result = datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S')
    result = result - datetime.timedelta(0,result.minute*60 + result.second,0)
    return result

# Converts an Angaza time with ms to a datetime format
def toTime_ms(angaza_time):
    result = datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S.%f')
    result = result - datetime.timedelta(0,result.minute*60 + result.second,result.microsecond)
    return result
    

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

# Returns the expected payment over the given period based on the plan
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

# Returns the expected disable date based on payment plan
# Solve issue with double payment the days of the activation
# Solve issue with full payments
def expect_disable(lastPay_date, lastPay_amount, activated, plan):
    days = 0
    if len(plan) != 1:
        if lastPay_date == activated:
            i = 1
            lastPay_amount -= plan[0]
            while lastPay_amount >= 0:
                lastPay_amount -= (plan[i] - plan[i-1])
                i += 1
                days += 7
        else:
            i = 1
            while lastPay_amount >= 0:
                lastPay_amount -= (plan[i] - plan[i-1])
                i += 1
                days += 7
            days -=7
    delta = datetime.timedelta(days,0,0)
    return lastPay_date + delta

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

print(chr(27))
print('############################################')
print('####### EASY SOLAR REPORTING TOOL V0 #######')
print('############################################')
print(chr(27))

# Defining the report's end date
question = input('Do you want to use TODAY as the end date for this reporting database? (y/n) ')
if question == 'y':
    report_end = datetime.datetime.today()
else:
    year = input(' Year? ')
    month = input(' Month? ')
    day = input(' Day? ')
    report_end = datetime.datetime(int(year),int(month),int(day),23,59,59,999999)
print(chr(27))

# Defining other important dates
report_start = datetime.datetime(2016,3,1,00,00,00,000000)
month_start = datetime.datetime(report_end.year,report_end.month,1,00,00,00,000000)
month_end = datetime.datetime(report_end.year,report_end.month+1,1,00,00,00,000000)
today = datetime.datetime.today()

# Generating the progress bar
bar = Bar('Generating Database', max=len(payments_raw))

# Creating the target dictionnary
data = {}

for j in range(0,(len(payments_raw))):
    i = len(payments_raw) - j - 1
    bar.next()
    # Defines the current payment for ease of coding
    pay = payments_raw[i]
    # Checking that the payment is whithing the report's range
    if toTime(pay['recorded_utc']) >= report_start and toTime(pay['recorded_utc']) <= report_end:
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
            line['pay_number_thisMonth'] += thisMonth(line['lastPay_date'],report_end)*1
            line['pay_thisMonth'] += thisMonth(line['lastPay_date'],report_end)*int(line['lastPay_amount'])
            line['pay_thisMonth_expected'] = expect_payment(report_start,month_end,line['reg_date'],plans[line['group_name']]) - (line['total_paid']-line['pay_thisMonth'])
            line['pay_thisMonth_expected_today'] = line['total_paid_expected'] - (line['total_paid']-line['pay_thisMonth'])
            # Complex calculations here (number of times disabeld etc.)
            line['disable_days_current'] = max(round(deltaToWeeks(line['lastPay_date']-line['next_disable_date'])*7,2),0)
            line['disable_days_total'].append(line['disable_days_current'])
            line['next_disable_date'] = expect_disable(line['lastPay_date'], line['lastPay_amount'], line['reg_date'], plans[line['group_name']])
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
            pay['lastPay_date'] = toTime(pay.pop('recorded_utc'))
            pay['total_paid'] = int(pay.pop('new_total_paid'))
            pay['account_angaza'] = pay.pop('account_angaza_id')
            # Adding the new dictionnary to the database
            data[account] = pay
            line = data[account]
            # Create the additional keys needed here
            line['pay_number'] = 1
            line['pay_number_thisMonth'] = thisMonth(line['lastPay_date'],report_end)*1
            line['reg_date'] = attributeFind(account, 'registration_date_utc')
            line['reg_date'] = toTime_ms(line['reg_date'])
            line['reg_agent'] = attributeFind(account, 'registering_user')
            line['product'] = attributeFind(account, 'attached_unit_type')
            line['lastlastPay_date'] = ''
            line['lastlastPay_amount'] = 0
            # Total expected payments
            line['total_paid_expected'] = expect_payment(report_start,report_end,line['reg_date'],plans[line['group_name']])
            # This month payments and expected
            line['pay_thisMonth'] = thisMonth(line['lastPay_date'],report_end)*line['lastPay_amount']
            line['pay_thisMonth_expected'] = expect_payment(report_start,month_end,line['reg_date'],plans[line['group_name']]) - (line['total_paid']-line['pay_thisMonth'])
            line['pay_thisMonth_expected_today'] = line['total_paid_expected'] - (line['total_paid']-line['pay_thisMonth'])
            line['disable_days_current'] = 0
            line['disable_days_total'] = []
            line['next_disable_date'] = expect_disable(line['lastPay_date'], line['lastPay_amount'], line['reg_date'], plans[line['group_name']])
            # Left to define
            line['sPoints']=expect_payment(report_start,report_end,line['reg_date'],points[line['group_name']])
            line['sPoints_thisMonth']=expect_payment(month_start,report_end,line['reg_date'],points[line['group_name']])
            line['disable_number']=0
            line['disable_days_over1']=0

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
    # Taking filter options from the user for the report
    choice_rm = input('Do you want to filter by Regional Manager? (y/n) ')
    if choice_rm == 'y':
        rm = input('Regional Manager name... ')
    choice_agent = input('Do you want to filter by agent? (y/n) ')
    if choice_agent == 'y':
        agent = input('Agent name... ')
    choice_model = input('Do you want to filter by lamp model? (y/n) ')
    if choice_model == 'y':
        model = input('Model name... ')
    choice_plan = input('Do you want to filter by payment plan? (y/n) ')
    if choice_plan == 'y':
        plan = input('Plan name... ')
    print(chr(27))
    print('>>>>> BEGIN NEW REPORT')
    print(chr(27))
    print(' Period ranging from ' + str(report_start) + ' to ' + str(report_end))
    # Printing fiter options
    if choice_agent == 'y':
        print(' For Regional Manager: ' + rm)
    else:
        print(' For ALL Regional Managers')
    if choice_agent == 'y':
        print(' For agent: ' + agent)
    else:
        print(' For ALL agents')
    if choice_model == 'y':
        print(' For model: ' + model)
    else:
        print(' For ALL lamp models')
    if choice_plan == 'y':
        print(' For payment plan: ' + plan)
    else:
        print(' For ALL payment plans')
    pay_collected = 0
    pay_expected = 0
    pay_number = 0
    pay_thisMonth = 0
    pay_thisMonth_expected = 0
    pay_number_thisMonth = 0
    for account in data:
        # Preparing filter variable depending on user defined filters
        select = 1
        # IMPLEMENT REGIONAL MANAGER FILTER
        if choice_agent == 'y':
            select *= (data[account]['reg_agent'] == agent)
        if choice_model == 'y':
            select *= (data[account]['product'] == model)
        if choice_plan == 'y':
            select *= (data[account]['group_name'] == plan)
        # Aggregating data if all filter criteria are met
        pay_collected += data[account]['total_paid']*select
        pay_expected += data[account]['total_paid_expected']*select
        pay_number += data[account]['pay_number']*select
        pay_thisMonth += data[account]['pay_thisMonth']*select
        pay_thisMonth_expected += data[account]['pay_thisMonth_expected']*select
        pay_number_thisMonth += data[account]['pay_number_thisMonth']*select
    print(chr(27))
    print(' Total collection: ' + str("{:,}".format(pay_collected)))
    print(' Expected amount collected: ' + str("{:,}".format(pay_expected)))
    if pay_expected == 0:
        ratio = 'n.a.'
    else:
        ratio = str(round(pay_collected/pay_expected,2)*100) + '%'
    print(' Total repayment ratio: ' + ratio)
    print(' Number of payments collected: ' + str(pay_number))
    if pay_number != 0:
        print(' Average payment amount: ' + str("{:,}".format(int(round(pay_collected/pay_number,0)))))
    print(chr(27))
    print(' Total amount collected this month: ' + str("{:,}".format(pay_thisMonth)))
    print(' Expected amount collected this month: ' + str("{:,}".format(pay_thisMonth_expected)))
    if pay_thisMonth_expected == 0:
        ratio = 'n.a.'
    else:
        ratio = str(round(pay_thisMonth/pay_thisMonth_expected,2)*100) + '%'
    print(' Repayment ratio this month so far: ' + ratio)
    print(' Number of payments collected this month: ' + str(pay_number_thisMonth))
    if pay_number_thisMonth != 0:
        print(' Average payment amount this month: ' + str("{:,}".format(int(round(pay_thisMonth/pay_number_thisMonth,0)))))
    print(chr(27))
    print('>>>>> END OF REPORT')

    print(chr(27))
    choice = input('Do you want to produce another report? (y/n) ')
    if choice == 'n':
        report = False

    for account in data:
        print(account)
        print(data[account])
