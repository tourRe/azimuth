from __future__ import absolute_import

from django.core.exceptions import ValidationError
from celery import app, shared_task
from sales.models import Client, Account, Payment, Agent
from inventory.models import (
        Product, Transaction, TransactionItem, InventoryItem, Warehouse
        )
from progress.bar import Bar
import csv, datetime
import pytz
import requests
from requests.auth import HTTPBasicAuth

@app.shared_task
def collect(online=False):

    print('Importing dump files')
    if online:
        login = 'op=alex@azimuth-solar.com'
        pw = 'raw=Lapoudre2009'
        url1 = 'https://payg.angazadesign.com/api/snapshots/accounts'
        url2 = 'https://payg.angazadesign.com/api/snapshots/payments'
        url3 = 'https://payg.angazadesign.com/api/snapshots/users'
        url4 = 'https://payg.angazadesign.com/api/snapshots/sms_messages'
        with requests.Session() as s:

            print(' > downloading accounts')
            download = s.get(url1, auth=(login,pw))
            decoded_content = download.content.decode('utf-8')
            accounts_raw = csvToList2(decoded_content.splitlines())

            print(' > downloading payments')
            download = s.get(url2, auth=(login,pw))
            decoded_content = download.content.decode('utf-8')
            payments_raw = csvToList2(decoded_content.splitlines())
    else:
        accounts_raw = csvToList('media/accounts.csv')
        payments_raw = csvToList('media/payments.csv')

    # List of updated clients + accounts to delete those not found in the dumps
    updated_clients = []
    updated_accounts = []
    updated_payments = []

    # IMPORTING ACCOUNTS

    bar = Bar('Updating Accounts', max=len(accounts_raw))

    for i in range(0,len(accounts_raw)):
        bar.next()
        j = len(accounts_raw) - i - 1
        acc_read = accounts_raw[i]

        # Identifying agent
        agent = Agent.objects.get(label = acc_read['responsible_user'])

        # Identifying product
        try: 
            product = Product.objects.get(
                    label = acc_read['attached_unit_type'])
        # in case the account is "detached", there is no 'attached_unit_type
        # the exception is catched in except and the rest of the loop is
        # skipped so that the account gets deleted
        except:
            pass

        # Creating or identifying client
        try: gender = acc_read['customer_gender'][0]
        except: gender = acc_read['customer_gender']
        # if the client exists (based on phone), updates info
        try:
            client = Client.objects.get(phone = acc_read['owner_msisdn'])
            client.name = acc_read['owner_name']
            client.gender = gender
            client.location = acc_read['location']
            client.save()
        # if not creates a new client
        except:
            client = Client.objects.create(
                    name = acc_read['owner_name'],
                    gender = gender,
                    phone = acc_read['owner_msisdn'],
                    location = acc_read['owner_location']
                    )
        updated_clients.append(client.phone)

        # Creating or identifying account
        # if the account exists (based on acc #), updates info
        try: 
            acc = Account.objects.get(
                account_Angaza = acc_read['angaza_id'])
            acc.account_GLP = acc_read['account_number']
            acc.client = client
            acc.plan_name = acc_read['group_name']
            # Can safely assume product type won't change
            # acc.plan_product = product
            acc.plan_up = int(acc_read['upfront_price'])
            acc.plan_tot = int(acc_read['unlock_price'])
            acc.plan_week = int(float(acc_read['hour_price'])*24*7)
            acc.reg_date = toDate_ms(acc_read['registration_date_utc'])
            acc.agent = agent
            if acc_read['account_status'] == 'Detached':
                acc.status = 'r'
            else:
                acc.status = acc_read['account_status'][0].lower()
        # otherwise creates a new account
        except:
            acc = Account(
                    account_Angaza = acc_read['angaza_id'],
                    account_GLP = acc_read['account_number'],
                    client = client,
                    plan_name = acc_read['group_name'],
                    plan_product = product,
                    plan_up = int(acc_read['upfront_price']),
                    plan_tot = int(acc_read['unlock_price']),
                    plan_week = int(float(acc_read['hour_price'])*24*7),
                    reg_date = toDate_ms(acc_read['registration_date_utc']),
                    agent = agent,
                    status = acc_read['account_status'][0].lower()
                    )
            try:
                acc.save()
            except ValidationError as e:
                # deleting the account in case tranItem couldn't be saved
                # this also deletes the related Transaction
                acc.delete()
                for key, value in e.message_dict.items():
                    print("error in " + key + ": " + value)

        updated_accounts.append(acc.account_Angaza)

    bar.finish()

    # IMPORTING PAYMENTS

    bar = Bar('Updating Payments', max=len(payments_raw))

    for i in range(0,len(payments_raw)):
        bar.next()
        j = len(payments_raw) - i - 1
        pay_read = payments_raw[j]

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
        updated_payments.append(pay.id_Angaza)
        pay.save()

    bar.finish()
    
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
