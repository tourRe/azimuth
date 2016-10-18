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

    # Preparing tables
    context['all_clients'] = Client.objects.all()
    context['all_accounts'] = Account.objects.all()
    context['all_payments'] = Payment.objects.all()

    return render(request, 'sales/index.html', context)

def manager_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    for manager in manager_list:
        key = ("<a href='/sales/managers/" + manager.firstname + "/'>"
                + " " + manager.firstname + " " + manager.lastname + "</a>")
        agents = Agent.objects.filter(manager = manager)
        account_table[key] = Account.objects.filter(agent__in = agents)
    context['account_table'] = account_table
    return render(request, 'sales/manager_index.html', context)

def manager(request, manager_firstname):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    manager = Manager.objects.get(firstname = manager_firstname)
    agents = Agent.objects.filter(manager = manager)
    for agent in agents:
        key = ("<a href='/sales/agents/" + agent.login + "/'>"
                + " " + agent.location + " (" + agent.firstname + " "
                + agent.lastname + ")</a>")
        account_table[key] = Account.objects.filter(agent=agent)
    context['account_table'] = account_table
    context['manager'] = manager
    return render(request, 'sales/manager.html', context)

def agent_index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list,
            }

    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    for agent in agent_list:
        key = ("<a href='/sales/agents/" + agent.login + "/'>"
                + " " + agent.location + " (" + agent.firstname + " "
                + agent.lastname + ")</a>")
        account_table[key] = Account.objects.filter(agent=agent)
    context['account_table'] = account_table
    return render(request, 'sales/agent_index.html', context)

def agent(request, agent_login):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    # Identifying agent and adding it to context
    agent = Agent.objects.get(login = agent_login)
    context['agent'] = agent

    # Adding PAR7 table to context
    par7_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled_current >= 7:
            key = acc.account_GLP + " (" + acc.account_Angaza + ")"
            par7_table[key] = acc
    context['par7_table'] = par7_table

    # Adding PDP14 table to context
    pdp14_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled >= 14:
            key = acc.account_GLP + " (" + acc.account_Angaza + ")"
            pdp14_table[key] = acc
    context['pdp14_table'] = pdp14_table

    # Adding PDP14 table to context
    pdp30_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled >= 30:
            key = acc.account_GLP + " (" + acc.account_Angaza + ")"
            pdp30_table[key] = acc
    context['pdp30_table'] = pdp30_table

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
