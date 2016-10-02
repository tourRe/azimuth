# Used to generated views withour HTTPResponse
from django.shortcuts import render
# Module that has the ordered dictionnary class
import collections
# Importing necessary models
from .models import Agent, Manager, Account

def index(request):
    # Adding menu content to context
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
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
        days_disabled += acc.get_current_disabled
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
