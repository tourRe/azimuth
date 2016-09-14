# TO DO
# > handle written off accounts
# > handle unlocked accounts (at least total)
# > implement regional manager tagging and filters
# > improve agent report with list of worst customers
# > improve agent report with way to distangle bad + good customers
# compensating
# > improve conversion to tinyDB performance

#!/usd/bin/env python3
import csv
import datetime
from tinydb import TinyDB, Query
from progress.bar import Bar

# Imports a CSV sheet and returns a list of dictionnaries
def csvToList(path):
    reader = csv.DictReader(open(path))
    result = []
    for dict in reader:
        result.append(dict)
    return result

# Searches through the accounts and return and attribute for the given account
def findInAccounts(account, attribute):
    # Investigate list indexing and list length...
    for i in range(0,(len(accounts_raw))):
        current_account = accounts_raw[i]
        if current_account['account_number'] == account:
            return current_account[attribute]

# Converts an UTC string to a datetime rounded at the previous hour
def toTime(angaza_time):
    result = datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S')
    # Removing the minutes and seconds
    result = result - datetime.timedelta(0,result.minute*60 + result.second,0)
    return result

# Converts a UTC string with ms to a datetime rounded at the previous hour
def toTime_ms(angaza_time):
    result = datetime.datetime.strptime(angaza_time,'%Y-%m-%d %H:%M:%S.%f')
    # Removing the minutes, seconds and microseconds
    result = result - datetime.timedelta(0,result.minute*60 + result.second,result.microsecond)
    return result

# Returns 1 if date is of today's month and year, 0 otherwise
def thisMonth(date, today):
    result = 0
    if date.year == today.year and date.month==today.month:
        result = 1
    return result

# Returns a datetime.timedelta in weeks with decimals
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
def expect_disable(next_disable_date, lastPay_date, lastPay_amount, total_paid, activated, plan):
    total_paid_before = total_paid - lastPay_amount
    days = 0
    if len(plan) != 1:
        weekly_rate = plan[1] - plan[0]
        if total_paid_before < plan[0]:
            if total_paid < plan[0]:
                days += (lastPay_amount/plan[0])*7
            else:
                days += ((plan[0] - total_paid_before)/plan[0])*7
                lastPay_amount -= (plan[0] - total_paid_before)
        else:
            i = 1
            while lastPay_amount >= weekly_rate:
                lastPay_amount -= weekly_rate
                i += 1
                days += 7
            days += lastPay_amount*7/weekly_rate
        days += max(0,deltaToWeeks(next_disable_date - lastPay_date)*7)
    delta = datetime.timedelta(days,0,0)
    return lastPay_date + delta

# Returns the number of solar points earned
def sPoints(total_paid,points):
    result = 0
    for key in points:
        if int(key) <= total_paid:
            result += points[key]
    return result

# Returns the sum of given fields in list of dictionnaries
def sumField(search,field_list):
    results = {}
    results['count'] = 0
    for j in range(0,len(field_list)):
        results[field_list[j]] = 0
    for i in range(0,len(search)):
        line = search[i]
        results['count'] += 1
        for j in range(0,len(field_list)):
            field_active = field_list[j]
            results[field_active] += line[field_active]
    return results

# Returns the ratio of two numbers as a string and handles errors
def ratio(top,bot):
    if bot == 0:
        ratio = 'n.a.'
    else:
        ratio = str(round(top/bot,2)*100) + '%'
    return ratio

# Returns the payment plan as a list
def build_plan(upfront,total,weekly):
    result = [upfront]
    if total != upfront:
        for i in range(1,int((total-upfront)/weekly) + 1):
            result.append(upfront + i*weekly)
    return result

# Adds an element to a list if not already there
def add_toList(item,plans):
    if len(plans) == 0:
        plans = [item]
    elif not(item in plans):
        plans.append(item)
    return plans

# DEFINITION OF PAYMENT PLANS
# Coding assumes that payment plan "period" is 7 days
# Coding assumes that the upfront payment lasts 7 days
plans = {}
plans['Eco-0-Pilot'] = build_plan(80000,80000,0)
plans['Eco-18-Pilot'] = build_plan(10000,100000,5000)
plans['Eco_Cash'] = build_plan(100000,100000,0)
plans['Eco_Weekly'] = build_plan(20000,120000,5000)
plans['Pro_Cash'] = build_plan(350000,350000,0)
plans['Pro_Weekly_Existing Customer'] = build_plan(40000,400000,10000)
plans['Pro_Weekly_New Customer'] = build_plan(100000,400000,10000)
plans['SHS_Cash'] = build_plan(950000,950000,0)
plans['SHS_Weekly_15_Existing Customer'] = build_plan(100000,1100000,15000)
plans['SHS_Weekly_15_New Customer'] = build_plan(250000,1100000,15000)
plans['SHS_Weekly_20_Existing Customer'] = build_plan(100000,1000000,20000)
plans['SHS_Weekly_20_New Customer'] = build_plan(250000,1000000,20000)
plans['SHS_Weekly_Agent'] = build_plan(15000,945000,15000)

# DEFINITION OF SOLAR POINTS SCHEDULE
points = {}
points['Eco-18-Pilot'] = {'100000':1}
points['Eco-0-Pilot'] = {'80000':1}
points['Eco_Cash'] = {'100000':1}
points['Eco_Weekly'] = {'120000':1}
points['Pro_Cash'] = {'350000':4}
points['Pro_Weekly_Existing Customer'] = {'400000':4}
points['Pro_Weekly_New Customer'] = {'400000':1}
points['SHS_Cash'] = {'950000':10}
points['SHS_Weekly_15_Existing Customer'] = {'550000':2,'1100000':6}
points['SHS_Weekly_15_New Customer'] = {'550000':2,'1100000':6}
points['SHS_Weekly_20_Existing Customer'] = {'500000':2,'1000000':8}
points['SHS_Weekly_20_New Customer'] = {'500000':2,'1000000':8}
points['SHS_Weekly_Agent'] = {'945000':0}

# IMPORT OF LATEST ANGAZA DOWNLOADS
accounts_raw = csvToList('accounts.csv')
payments_raw = csvToList('payments.csv')

# SETUP OF VARIABLES TO COLLECT LISTS
agents_plans = {}

print(chr(27))
print('############################################')
print('####### EASY SOLAR REPORTING TOOL V0 #######')
print('############################################')
print(chr(27))

# Defining the report's end date
today = datetime.datetime.today()
question = input('Do you want to use TODAY as the end date for this reporting database? (y/n) ')
if question == 'y':
    report_end = today - datetime.timedelta(0,0,today.microsecond)
else:
    year = input(' Year? ')
    month = input(' Month? ')
    day = input(' Day? ')
    report_end = datetime.datetime(int(year),int(month),int(day),23,59,59,000000)
print(chr(27))

# Defining other important dates
report_start = datetime.datetime(2016,3,1,00,00,00,000000)
month_start = datetime.datetime(report_end.year,report_end.month,1,00,00,00,000000)
month_end = datetime.datetime(report_end.year,report_end.month+1,1,00,00,00,000000)

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
            line['paid'] = int(pay['new_total_paid'])
            line['pay_number'] += 1
            line['pay_number_thisMonth'] += thisMonth(line['lastPay_date'],report_end)*1
            line['paid_thisMonth'] += thisMonth(line['lastPay_date'],report_end)*int(line['lastPay_amount'])
            line['paid_thisMonth_expected'] = expect_payment(report_start,month_end,line['reg_date'],plans[line['group_name']]) - (line['paid']-line['paid_thisMonth'])
            line['paid_thisMonth_expected_today'] = line['paid_expected'] - (line['paid']-line['paid_thisMonth'])
            # Complex calculations here (number of times disabeld etc.)
            line['disabled_days_history'].append(max(round(deltaToWeeks(line['lastPay_date']-line['next_disable_date'])*7,2),0))
            line['pay_history'].append(line['lastPay_amount'])
            line['next_disable_date'] = expect_disable(line['next_disable_date'],line['lastPay_date'], line['lastPay_amount'], line['paid'], line['reg_date'], plans[line['group_name']])
            if line['paid'] == plans[line['group_name']][len(plans[line['group_name']])-1]:
                line['disabled_days_current'] = 0
                line['status'] = 'unlocked'
            else:
                line['disabled_days_current'] = max(0,deltaToWeeks(report_end - line['next_disable_date'])*7)
                if line['disabled_days_current'] == 0:
                    line['status'] = 'active'
                else:
                    line['status'] = 'disabled'
            sPoints_before = line['sPoints']
            line['sPoints'] = sPoints(line['paid'],points[line['group_name']])
            line['sPoints_thisMonth'] += (line['sPoints']-sPoints_before)*thisMonth(line['lastPay_date'],report_end)
        else:
            # Creating the account in the database
            account = pay['account']
            # Deleting useless keys in the dictionnary
            del pay['organization']
            del pay['angaza_id']
            del pay['country']
            del pay['reversal']
            del pay['provider_transaction']
            del pay['synced']
            del pay['recorder']
            del pay['type']
            del pay['applied_utc'] # only keeping recorded date
            # Converting and renaming keys in the dictionnary
            pay['account_angaza'] = pay.pop('account_angaza_id')
            pay['lastPay_amount'] = int(pay.pop('amount'))
            pay['lastPay_date'] = toTime(pay.pop('recorded_utc'))
            pay['paid'] = int(pay.pop('new_total_paid'))
            # Adding the new dictionnary to the database
            data[account] = pay
            line = data[account]
            # Create the additional keys needed here
            line['pay_number'] = 1
            line['pay_number_thisMonth'] = thisMonth(line['lastPay_date'],report_end)*1
            line['reg_date'] = findInAccounts(account, 'registration_date_utc')
            line['reg_date'] = toTime_ms(line['reg_date'])
            line['reg_agent'] = findInAccounts(account, 'registering_user')
            line['product'] = findInAccounts(account, 'attached_unit_type')
            line['lastlastPay_date'] = ''
            line['lastlastPay_amount'] = 0
            # Total expected payments
            line['paid_expected'] = expect_payment(report_start,report_end,line['reg_date'],plans[line['group_name']])
            # This month payments and expected
            line['paid_thisMonth'] = thisMonth(line['lastPay_date'],report_end)*line['lastPay_amount']
            line['paid_thisMonth_expected'] = expect_payment(report_start,month_end,line['reg_date'],plans[line['group_name']]) - (line['paid']-line['paid_thisMonth'])
            line['paid_thisMonth_expected_today'] = line['paid_expected'] - (line['paid']-line['paid_thisMonth'])
            line['next_disable_date'] = expect_disable(line['reg_date'],line['lastPay_date'], line['lastPay_amount'], line['paid'], line['reg_date'], plans[line['group_name']])
            if line['paid'] == plans[line['group_name']][len(plans[line['group_name']])-1]:
                line['disabled_days_current'] = 0
                line['status'] = 'unlocked'
            else:
                line['disabled_days_current'] = max(0,deltaToWeeks(report_end - line['next_disable_date'])*7)
                if line['disabled_days_current'] == 0:
                    line['status'] = 'active'
                else:
                    line['status'] = 'disabled'
            line['status']
            line['disabled_days_history'] = [0]
            line['pay_history'] = [line['lastPay_amount']]
            line['sPoints'] = sPoints(line['paid'],points[line['group_name']])
            line['sPoints_thisMonth'] = line['sPoints']*thisMonth(line['lastPay_date'],report_end)
            if not(line['reg_agent'] in agents_plans):
                agents_plans[line['reg_agent']] = []
            agents_plans[line['reg_agent']] = add_toList(line['group_name'],agents_plans[line['reg_agent']])
bar.finish()

# CAN BE OPTIMIZED BY SPECIFYING FIELDS TO TRANSLATE FROM DATETIME TO STRING
bar = Bar('Converting into TinyDB', max=len(data))
# Transferring data into tinyDB
db = TinyDB('db.json')
db.purge()
for account in data:
    bar.next()
    for key in data[account]:
        if isinstance(data[account][key],datetime.datetime):
            data[account][key] = data[account][key].isoformat()
    db.insert(data[account])
bar.finish()

# GENERATING REPORTS
print(chr(27))
report = True
while report:

    # Setting up type of report
    print('Which report would you like to see? ')
    report_type = input('rm = Regional Manager, a = Agent, g = general ')
    # Regional manager report
    if report_type == 'rm':
        rm = input('Regional manager name... ')
    # Agent report
    elif report_type == 'a':
        agent = input('Agent name... ')
    # Taking filter options for the General report
    elif report_type == 'g':
        choice_rm = input('Do you want to filter by regional manager? (y/n) ')
        rm = '\w'
        if choice_rm == 'y':
            rm = input('Regional manager name... ')
        choice_agent = input('Do you want to filter by agent? (y/n) ')
        agent = '\w'
        if choice_agent == 'y':
            agent = input('Agent name... ')
        choice_model = input('Do you want to filter by lamp model? (y/n) ')
        model = '\w'
        if choice_model == 'y':
            model = input('Model name... ')
        choice_plan = input('Do you want to filter by payment plan? (y/n) ')
        plan = '\w'
        if choice_plan == 'y':
            plan = input('Plan name... ')

    print(chr(27))
    print('############# BEGIN NEW REPORT #############')
    print(chr(27))
    print(' Period ranging from ' + str(report_start) + ' to ' + str(report_end))

    # GENERAL REPORT
    if report_type == 'g':
        if choice_agent == 'y': print(' For regional manager: ' + rm)
        else: print(' For ALL regional managers')
        if choice_agent == 'y': print(' For agent: ' + agent)
        else: print(' For ALL agents')
        if choice_model == 'y': print(' For model: ' + model)
        else: print(' For ALL lamp models')
        if choice_plan == 'y': print(' For payment plan: ' + plan)
        else: print(' For ALL payment plans')

        # Running Query and gathering results
        Account = Query()
        search = db.search((Account.reg_agent.matches(agent)) & (Account.product.matches(model)) & (Account.group_name.matches(plan)))
        results = sumField(search, ['paid','paid_expected','pay_number','paid_thisMonth','paid_thisMonth_expected','pay_number_thisMonth','sPoints','sPoints_thisMonth'])
        count = results['count']
        paid = results['paid']
        paid_expected = results['paid_expected']
        pay_number = results['pay_number']
        sPoints = results['sPoints']
        paid_thisMonth = results['paid_thisMonth']
        paid_thisMonth_expected = results['paid_thisMonth_expected']
        pay_number_thisMonth = results['pay_number_thisMonth']
        sPoints_thisMonth = results['sPoints_thisMonth']
        search = db.search((Account.reg_agent.matches(agent)) & (Account.product.matches(model)) & (Account.group_name.matches(plan)) & (Account.status == 'disabled'))
        results = sumField(search, ['paid'])
        disabled_number = results['count']

        # Printing results
        print(chr(27))
        print(' Number of accounts in this report: ' + str(count))
        print(' > including ' + str(disabled_number) + ' disabled accounts')
        print(chr(27))
        print(' Total collection: ' + str("{:,}".format(paid)))
        print(' Expected amount collected: ' + str("{:,}".format(paid_expected)))
        print(' Total repayment ratio: ' + ratio(paid,paid_expected))
        print(' Number of payments collected: ' + str(pay_number))
        if pay_number != 0:
            print(' Average payment amount: ' + str("{:,}".format(int(round(paid/pay_number,0)))))
        print(' Total number of Solar Points awarded: ' + str(sPoints))
        print(chr(27))
        print(' Total amount collected this month: ' + str("{:,}".format(paid_thisMonth)))
        print(' Expected amount collected this month: ' + str("{:,}".format(paid_thisMonth_expected)))
        print(' Repayment ratio this month so far: ' + ratio(paid_thisMonth,paid_thisMonth_expected))
        print(' Number of payments collected this month: ' + str(pay_number_thisMonth))
        if pay_number_thisMonth != 0:
            print(' Average payment amount this month: ' + str("{:,}".format(int(round(paid_thisMonth/pay_number_thisMonth,0)))))
        print(' Number of Solar Points awarded this month: ' + str(sPoints_thisMonth))
        print(chr(27))
    
    # REGIONAL MANAGER REPORT
    if report_type == 'rm':
        print(' Regional Manager report for: ' + rm)

    # AGENT REPORT
    if report_type == 'a':
        # Querying the database
        Account = Query()
        agent = '.*' + agent + '.*'
        search = db.search(Account.reg_agent.matches(agent))
        agent_name = search[0]['reg_agent']
        results = sumField(search, ['paid','paid_expected','pay_number','paid_thisMonth','paid_thisMonth_expected','pay_number_thisMonth','sPoints','sPoints_thisMonth'])
        count = results['count']
        paid = results['paid']
        paid_expected = results['paid_expected']
        pay_number = results['pay_number']
        sPoints = results['sPoints']
        paid_thisMonth = results['paid_thisMonth']
        paid_thisMonth_expected = results['paid_thisMonth_expected']
        pay_number_thisMonth = results['pay_number_thisMonth']
        sPoints_thisMonth = results['sPoints_thisMonth']
        search = db.search((Account.reg_agent.matches(agent)) & (Account.status == 'disabled'))
        results = sumField(search, ['paid'])
        disabled_number = results['count']

        # Printing results
        print(' Agent report for: ' + agent_name)
        print(chr(27))
        print(' Number of accounts for this agent: ' + str(count))
        print(' > including ' + str(disabled_number) + ' disabled accounts')
        print(chr(27))
        print(' Monthly summary')
        print(' > Total amount collected: ' + str("{:,}".format(paid_thisMonth)))
        print(' > Expected amount collected: ' + str("{:,}".format(paid_thisMonth_expected)))
        print(' > Repayment ratio so far: ' + ratio(paid_thisMonth,paid_thisMonth_expected))
        print(' > Number of payments collected: ' + str(pay_number_thisMonth))
        if pay_number_thisMonth != 0:
            print(' > Average payment amount: ' + str("{:,}".format(int(round(paid_thisMonth/pay_number_thisMonth,0)))))
        print(' > Number of Solar Points awarded: ' + str(sPoints_thisMonth))
        print(chr(27))

        print(' Breakdown by payment plan (collected || expected || ratio)')
        for plan in agents_plans[agent_name]:
            search = db.search((Account.reg_agent.matches(agent)) & (Account.group_name == plan))
            results = sumField(search, ['paid','paid_expected','pay_number','paid_thisMonth','paid_thisMonth_expected','pay_number_thisMonth','sPoints','sPoints_thisMonth'])
            count = results['count']
            paid = results['paid']
            paid_expected = results['paid_expected']
            pay_number = results['pay_number']
            sPoints = results['sPoints']
            paid_thisMonth = results['paid_thisMonth']
            paid_thisMonth_expected = results['paid_thisMonth_expected']
            paid_number_thisMonth = results['pay_number_thisMonth']
            Points_thisMonth = results['sPoints_thisMonth']
            search = db.search((Account.reg_agent.matches(agent)) & (Account.group_name == plan) & (Account.status == 'disabled'))
            results = sumField(search, ['paid'])
            disabled_number = results['count']
            print(" > " + str(plan) + ": " + str("{:,}".format(paid_thisMonth)) + ' || ' + str("{:,}".format(paid_thisMonth_expected)) + ' || ' + ratio(paid_thisMonth,paid_thisMonth_expected))
        print(chr(27))

    print('############## END OF REPORT ###############')
    print(chr(27))
    choice = input('Do you want to produce another report? (y/n) ')
    if choice == 'n':
        report = False
