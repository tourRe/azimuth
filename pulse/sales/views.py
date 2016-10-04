# Used to generated views withour HTTPResponse
from django.shortcuts import render
# Module that has the ordered dictionnary class
import collections
# Modules to handle dates and timwezones
import datetime, pytz
# Importing necessary models
from .models import Agent, Manager, Account, Client, Payment

def index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    # Preparing Clients table
    table_clients = collections.OrderedDict()
    Q = Client.objects.all()
    table_clients['Number'] = Q.count()
    table_clients['New this month'] = 0
    table_clients['New last month'] = 0
    for c in Q:
        table_clients['New this month'] += (c.get_new_TM)*1
        table_clients['New last month'] += (c.get_new_LM)*1
    table_clients['Accounts per client'] = ratio(
            Account.objects.all().count(),table_clients['Number'],False,2)
    # Converting numbers to well presented strings
    table_clients['Number'] = str("{:,}".format(
        table_clients['Number']))
    table_clients['New this month'] =  str("{:,}".format(
        table_clients['New this month']))
    table_clients['New last month'] =  str("{:,}".format(
        table_clients['New last month']))

    context['table_clients'] = table_clients

    # Preparing Accounts table
    table_accounts = collections.OrderedDict()
    Q = Account.objects.all()
    table_accounts['Number'] = Q.count()
    table_accounts['New this month'] = 0
    table_accounts['New last month'] = 0
    oar_14 = 0
    outstanding = 0
    for a in Q:
        table_accounts['New this month'] += (a.get_new_TM)*1
        table_accounts['New last month'] += (a.get_new_LM)*1
        oar_14 += a.OAR(14)
        outstanding += a.plan_tot - a.get_paid
    table_accounts['New this month'] =  str("{:,}".format(
        table_accounts['New this month']))
    table_accounts['New last month'] =  str("{:,}".format(
        table_accounts['New last month']))
    table_accounts['PAR (14 days)'] = ratio(
            oar_14,outstanding,True,2)
    context['table_accounts'] = table_accounts
    
    # Preparing Payments table
    table_payments = collections.OrderedDict()
    Q = Payment.objects.all()
    table_payments['Number'] = str("{:,}".format(Q.count()))
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    today_m2m = today - datetime.timedelta(62,0,0)
    Q2 = Payment.objects.filter(date__gt = today_m2m)
    table_payments['Collected this month'] = 0
    table_payments['Collected last month'] = 0
    for p in Q2:
        table_payments['Collected this month'] += (p.get_TM)*1
        table_payments['Collected last month'] += (p.get_LM)*1
    table_payments['Collected this month'] =  str("{:,}".format(
        table_payments['Collected this month']))
    table_payments['Collected last month'] =  str("{:,}".format(
        table_payments['Collected last month']))
    # Check online for averaging a field
    # table_payments['Average payment amount'] = str("{:,}".format(
    # Q.amount__average))
    table_payments['Average payment amount'] = "tbd"
    context['table_payments'] = table_payments

    return render(request, 'sales/index.html', context)

def manager_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/manager_index.html', context)

def manager(request, manager_firstname):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/manager.html', context)

def agent_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/agent_index.html', context)

def agent(request, agent_login):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/agent.html', context)

def client_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/client_index.html', context)

def client(request, client_pk):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/client.html', context)

def account_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    # Preparing data for global summary
    table_1 = collections.OrderedDict()
    account_number = Account.objects.all().count()
    table_1['Number of accounts'] = str("{:,}".format(
        account_number))
    table_1['... of which unlocked'] = str("{:,}".format(
            Account.objects.filter(status='u').count()))
    table_1['... of which enabled'] = str("{:,}".format(
            Account.objects.filter(status='e').count()))
    table_1['... of which disabled'] = str("{:,}".format(
            Account.objects.filter(status='d').count()))
    table_1['... of which written off'] = str("{:,}".format(
            Account.objects.filter(status='w').count()))
    paid = 0
    paid_expected = 0
    payment_deficit = 0
    days_disabled = 0
    pay_number = 0
    outstanding = 0
    oar_14 = 0
    for acc in Account.objects.all():
        paid += acc.get_paid
        paid_expected += acc.get_paid_expected
        payment_deficit += max(0,acc.get_pay_deficit)
        days_disabled += acc.days_disabled()
        pay_number += acc.get_pay_nb
        outstanding += acc.plan_tot - acc.get_paid
        oar_14 += acc.OAR(14)
    table_1['Total paid (SLL)'] = str("{:,}".format(paid))
    table_1['Repayment ratio (CRR)'] = ratio(paid,paid_expected,pc=True)
    table_1['Number of payments'] = str("{:,}".format(pay_number))
    table_1['Average payment (SLL)'] = ratio(paid,pay_number)
    table_1['PAR (14 days)'] = ratio(oar_14,outstanding,pc=True,dec=2)
    table_1['Average days disabled'] = ratio(days_disabled,account_number)
    table_1['Average unit price (SLL)'] = ratio(paid+outstanding,account_number)
    context['table_1']=table_1

    # Preparing data for monthly summary
    table_2 = collections.OrderedDict()
    account_number = 0 
    paid = 0
    paid_expected = 0
    payment_deficit = 0
    days_disabled = 0
    pay_number = 0
    outstanding = 0
    oar_14 = 0
    for acc in Account.objects.all():
        if acc.get_new_LM:
            account_number += 1
            paid += acc.get_paid
            paid_expected += acc.get_paid_expected
            payment_deficit += max(0,acc.get_pay_deficit)
            days_disabled += acc.days_disabled()
            pay_number += acc.get_pay_nb
            outstanding += acc.plan_tot - acc.get_paid
            oar_14 += acc.OAR(14)
    table_2['Number of accounts'] = str("{:,}".format(account_number))
    table_2['Total paid (SLL)'] = str("{:,}".format(paid))
    table_2['Repayment ratio (CRR)'] = ratio(paid,paid_expected,pc=True)
    table_2['Number of payments'] = str("{:,}".format(pay_number))
    table_2['Average payment (SLL)'] = ratio(paid,pay_number)
    table_2['PAR (14 days)'] = ratio(oar_14,outstanding,pc=True,dec=2)
    table_2['Average days disabled'] = ratio(days_disabled,account_number)
    table_2['Average unit price (SLL)'] = ratio(paid+outstanding,account_number)
    context['table_2']=table_2

    # Generating data per plan
    table_3 = {}
    for acc in Account.objects.all():
        if not (acc.plan_name in table_3.keys()):
            table_3[acc.plan_name] = [0,0,0,0,0,0]
        table_3[acc.plan_name][0] += acc.get_paid_TM
        table_3[acc.plan_name][1] += (acc.status == 'e')*1
        table_3[acc.plan_name][2] += (acc.status == 'd')*1
        table_3[acc.plan_name][3] += (acc.status == 'u')*1
        table_3[acc.plan_name][4] += acc.OAR(14)
        table_3[acc.plan_name][5] += acc.plan_tot - acc.get_paid
    for key in table_3:
        table_3[key][4] = ratio(table_3[key][4],table_3[key][5],True,2)
        del table_3[key][-1]
    context['table_3']=table_3

    return render(request, 'sales/account_index.html', context)

def account(request, account_Angaza):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/account.html', context)

def payment_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/payment_index.html', context)

def ratio(top, bottom, pc=False, dec=0):
    if bottom == 0:
        return "n.a."
    elif pc:
        if dec == 0:
            return str(int(round(top/bottom,2)*100)) + " %"
        else:
            return str(round(top/bottom,2+dec)*100) + " %"
    else:
        if dec == 0:
            return str("{:,}".format(int(round(top/bottom,0))))
        else:
            return str("{:,}".format(round(top/bottom,dec)))
