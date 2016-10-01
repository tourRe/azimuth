from __future__ import absolute_import

from celery import app, shared_task
from sales.models import Client, Account, Payment, Agent
from inventory.models import Product
import csv, datetime
import pytz

@app.shared_task
def collect():
    accounts_raw = csvToList('media/accounts.csv')
    payments_raw = csvToList('media/payments.csv')

    for i in range(0,len(accounts_raw)):
        j = len(accounts_raw) - i - 1
        acc_read = accounts_raw[j]

        # Identifying agent
        agent = Agent.objects.get(label = acc_read['responsible_user'])

        # Identifying product
        product = Product.objects.get(label = acc_read['attached_unit_type'])

        # Creating or identifying client
        try: gender = acc_read['customer_gender'][0]
        except: gender = acc_read['customer_gender']
        client, created = Client.objects.get_or_create(
                name = acc_read['owner_name'],
                gender = gender,
                phone = acc_read['owner_msisdn'],
                location = acc_read['location']
                )
        client.save()

        # Creating or identifying account
        acc, created = Account.objects.get_or_create(
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
        acc.save()

def csvToList(path):
    reader = csv.DictReader(open(path))
    result = []
    for dict in reader:
        result.append(dict)
    return result

def toDate(date):
    result = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    result = result - datetime.timedelta(0,result.minute*60 + result.second,0)
    result = result.replace(tzinfo=pytz.utc)
    return result

def toDate_ms(date):
    result = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
    result = result - datetime.timedelta(0,result.minute*60 + result.second,0)
    result = result.replace(tzinfo=pytz.utc)
    return result
