from __future__ import absolute_import

from django.core.exceptions import ValidationError
from celery import app, shared_task
from sales.models import Client, Account, Payment, Agent
from system.models import Update
from inventory.models import (
        Product, Transaction, TransactionItem, InventoryItem, Warehouse
        )
from progress.bar import Bar
import csv, datetime, pytz, requests
from requests.auth import HTTPBasicAuth

today = datetime.datetime.today().replace(tzinfo=pytz.utc)

@app.shared_task
def fetch_data(force_full = False, online = True):

    # DOWNLOADING/IMPORTING RAW ANGAZA FILES

    print('Importing dump files')
    if not online:
        print(' > Fetching dump files in Media folder...')
        accounts_raw = csvToList('media/accounts.csv')
        payments_raw = csvToList('media/payments.csv')
        users_raw = csvToList('media/users.csv')

    else:
        print(' > Fetching dump files online...')
        login = 'op=alex@azimuth-solar.com'
        pw = 'raw=Lapoudre2009'
        url1 = 'https://payg.angazadesign.com/api/snapshots/accounts'
        url2 = 'https://payg.angazadesign.com/api/snapshots/payments'
        url3 = 'https://payg.angazadesign.com/api/snapshots/users'
        url4 = 'https://payg.angazadesign.com/api/snapshots/sms_messages'
        url5 = 'https://payg.angazadesign.com/api/organizations/OR000029'
        with requests.Session() as s:
            print(' > downloading users')
            download = s.get(url3, auth=(login,pw))
            decoded_content = download.content.decode('utf-8')
            users_raw = csvToList2(decoded_content.splitlines())
            print(' > downloading accounts')
            download = s.get(url1, auth=(login,pw))
            decoded_content = download.content.decode('utf-8')
            accounts_raw = csvToList2(decoded_content.splitlines())
            print(' > downloading payments')
            download = s.get(url2, auth=(login,pw))
            decoded_content = download.content.decode('utf-8')
            payments_raw = csvToList2(decoded_content.splitlines())

    # SETTING UP COUNTERS TO TRACK UPDATE ACTIONS 
    
    updated_clients = []
    updated_accounts = []
    updated_payments = []
    new_agents = 0
    new_clients = 0
    new_accounts = 0
    new_payments = 0

    print('Updating database')

    # SETTING UP UPDATE PARAMETERS

    updates = Update.objects.all()
    if not updates: 
        full = True
        hours_since = 24
        print(' > No previous update > Forcing full update')
    elif force_full: 
        full = True
        hours_since = updates.last_update().hours_since
        print(' > Forcing full update')
    else:
        last_full_update = updates.last_full_update()
        hours_since_full = last_full_update.hours_since
        print(' > Time since last full update: ' +
                str(round(hours_since_full,2)) + 'h')
        full = hours_since_full >= 24
        last_update = updates.last_update()
        hours_since = last_update.hours_since

    if full:
        nb_pays = len(payments_raw)
        print(' > Full update...')
    else:
        nb_pays = max(int(last_update.new_pays / last_update.hours * 
            last_update.hours_since * 5),100)
        print(' > partial update for last ' + str(nb_pays) + ' payments...')

    pays_start = max(0,len(payments_raw) - nb_pays)

    # UPDATING AGENTS

    bar = Bar('Updating Agents', max=len(users_raw))

    for i in range(0,len(users_raw)):
        bar.next()

        usr_read = users_raw[i]

        try: 
            agent = Agent.objects.get(uid = usr_read['angaza_id'])
            agent.firstname = usr_read['first_name']
            agent.lastname = usr_read['last_name']
            agent.phone = usr_read['primary_phone']
            agent.login = usr_read['email']
            agent.label = '%s %s (%s)' %(usr_read['first_name'],
                    usr_read['last_name'], usr_read['email'])
            agent.save()

        except:
            agent = Agent.objects.create(
                    uid = usr_read['angaza_id'],
                    firstname = usr_read['first_name'],
                    lastname = usr_read['last_name'],
                    phone = usr_read['primary_phone'],
                    start_date = toDate(usr_read['created_utc']),
                    login = usr_read['email'],
                    label = '%s %s (%s)' %(usr_read['first_name'],
                            usr_read['last_name'],
                            usr_read['email'])
                    )
            new_agents += 1

    bar.finish()

    # UPDATING CLIENTS AND ACCOUNTS

    bar = Bar('Updating Accounts', max=len(accounts_raw))

    for i in range(0,len(accounts_raw)):
        bar.next()
        
        acc_read = accounts_raw[i]

        # Identifying responsible agent
        agent = Agent.objects.get(label = acc_read['responsible_user'])

        # Identifying attached product
        try: product = Product.objects.get(
                label = acc_read['attached_unit_type'])
        except: 
            product = Product.objects.create(
                    name = acc_read['attached_unit_name'],
                    label = acc_read['attached_unit_type'])

        # Computing account status
        status_db = acc_read['account_status']
        if status_db == 'DETACHED':
            status = 'r'
        else:
            status = status_db[0].lower()

        updated_clients.append(client.phone)

        # EXISTING ACCOUNT
        try: 
            acc = Account.objects.get(
                account_Angaza = acc_read['angaza_id'])
            acc.account_GLP = acc_read['account_number']
            acc.agent = agent
            acc.client = client
            acc.plan_name = acc_read['group_name']
            acc.plan_up = int(acc_read['upfront_price'])
            acc.plan_tot = int(acc_read['unlock_price'])
            acc.plan_week = int(float(acc_read['hour_price'])*24*7)
            acc.plan_iscash = (acc.plan_up == acc.plan_tot)
            if status_db in ['r', 'w'] and acc.status not in ['r', 'w', 'u']:
                acc.unlock_date = today
            acc.status = status

        # NEW ACCOUNT
        except:

            # If the client exists (based on phone), updates info
            try:
                client = Client.objects.get(phone = acc_read['owner_msisdn'])
                client.name = acc_read['owner_name']
                try: client.gender = acc_read['customer_gender'][0]
                except: pass
                client.location = acc_read['location']
                client.save()
            # If not creates a new client
            except:
                client = Client.objects.create(
                        name = acc_read['owner_name'],
                        phone = acc_read['owner_msisdn'],
                        location = acc_read['location'])
                try: client.gender = acc_read['customer_gender'][0]
                except: pass
                client.save()
                new_clients += 1

            # Creates the account
            acc = Account.objects.create(
                    # static parameters
                    account_Angaza = acc_read['angaza_id'],
                    reg_date = toDate(acc_read['registration_date_utc']),
                    plan_product = product,
                    # dynamic parameters
                    account_GLP = acc_read['account_number'],
                    agent = agent,
                    status = status,
                    plan_name = acc_read['group_name'],
                    plan_up = int(acc_read['upfront_price']),
                    plan_tot = int(acc_read['unlock_price']),
                    plan_week = int(float(acc_read['hour_price'])*24*7),
                    client = client,
                    # convenience parameters
                    plan_iscash = (int(acc_read['upfront_price']) == 
                        int(acc_read['unlock_price'])),
                    )
            new_accounts += 1

        updated_accounts.append(acc.account_Angaza)

    bar.finish()

    # IMPORTING PAYMENTS

    bar = Bar('Updating Payments', max=(len(payments_raw)-pays_start))

    for i in range(pays_start,len(payments_raw)):
        bar.next()
        pay_read = payments_raw[i]

        # Identifying agent
        agent = Agent.objects.get(login = pay_read['recorder'])

        # Identifying account
        acc = Account.objects.get(
                account_Angaza = pay_read['account_angaza_id'])
        try:
            pay = Payment.objects.get(
                    id_Angaza = pay_read['angaza_id'])
            if pay_read['reversal'] != 'None':
                pay.delete()
            else:
                pay.account = acc
                pay.amount = int(pay_read['amount'])
                pay.date = toDate(pay_read['recorded_utc'])
                pay.agent = agent
        except:
            if pay_read['reversal'] == 'None':
                pay = Payment(
                        account = acc,
                        amount = int(pay_read['amount']),
                        date = toDate(pay_read['recorded_utc']),
                        agent = agent,
                        id_Angaza = pay_read['angaza_id']
                        )
                new_payments += 1
        updated_payments.append(pay.id_Angaza)
        pay.save()

    bar.finish()

    Update.objects.create(date=today,is_full=full,hours=hours_since,
            new_clients = new_clients,
            new_accs = new_accounts,
            new_pays = new_payments)

    print('Update summary:')
    print(' > ' + str(new_clients) + ' new clients created')
    print(' > ' + str(new_accounts) + ' new accounts created')
    print(' > ' + str(new_payments) + ' new payments created')
    
    if full:
        # Deleting all clients (+ accounts) not found in the dump
        print('Deleting deprecated entries')
        print(' > deleting {} clients'.format(
            Client.objects.exclude(phone__in = updated_clients).count()))
        Client.objects.exclude(phone__in = updated_clients).delete()
        print(' > deleting {} accounts'.format(
            Account.objects.exclude(account_Angaza__in = updated_accounts).count()))
        Account.objects.exclude(account_Angaza__in = updated_accounts).delete()
        print(' > deleting {} payments'.format(
            Payment.objects.exclude(id_Angaza__in = updated_payments).count()))
        Payment.objects.exclude(id_Angaza__in = updated_payments).delete()

def csvToList(path):
    reader = csv.DictReader(open(path))
    result = []
    for dict in reader:
        result.append(dict)
    return result

def csvToList2(path):
    reader = csv.DictReader(path, delimiter=',')
    result = []
    for dict in reader:
        result.append(dict)
    return result

def toDate(date):
    result = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    result = result.replace(tzinfo=pytz.utc)
    return result

def toDate_ms(date):
    result = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
    result = result.replace(tzinfo=pytz.utc)
    return result
