# Used to generated views without HTTPResponse and generate the graphs
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
# Module that has the ordered dictionnary class
import collections
# Modules to handle dates and timwezones
import datetime, pytz
# Importing necessary models
from .models import Agent, Manager, Account, Client, Payment
from inventory.models import Product

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

    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    products = Product.objects.all()
    accounts = Account.objects.filter(agent = agent)
    for prod in products:
        account_table[prod.name] = accounts.filter(plan_product = prod)
    context['account_table'] = account_table

    # Adding PAR7 table to context
    par7_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled_current >= 7:
            key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                    + " " + acc.account_GLP + " (" + acc.account_Angaza 
                    + ")</a>")
            par7_table[key] = acc
    context['par7_table'] = par7_table

    # Adding PDP14 table to context
    pdp14_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled >= 14:
            key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                    + " " + acc.account_GLP + " (" + acc.account_Angaza 
                    + ")</a>")
            pdp14_table[key] = acc
    context['pdp14_table'] = pdp14_table

    # Adding PDP14 table to context
    pdp30_table = collections.OrderedDict()
    Q = Account.objects.filter(agent=agent).order_by('account_GLP')
    for acc in Q:
        if acc.is_active and acc.days_disabled >= 30:
            key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                    + " " + acc.account_GLP + " (" + acc.account_Angaza 
                    + ")</a>")
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
    client = Client.objects.get(pk = client_pk)
    context['client'] = client

    # Adding related accounts to context
    related_accounts = collections.OrderedDict()
    Q = Account.objects.filter(client=client).order_by('account_GLP')
    for acc in Q:
        key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                + " " + acc.account_GLP + " (" + acc.account_Angaza 
                + ")</a>")
        related_accounts[key] = acc
    context['related_accounts'] = related_accounts
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
    account = Account.objects.get(account_Angaza = account_Angaza)
    context['account'] = account
    return render(request, 'sales/account.html', context)

def payment_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }

    return render(request, 'sales/payment_index.html', context)

#***************************************************************
#************************* GRAPHS ******************************
#***************************************************************

def payment_season_hour(request):
    payments = Payment.objects.all()
    #Computing the nb of payments per week
    parse = [0] * 24
    for pay in payments:
        index = pay.date.hour
        parse[index] += 1
    #Format
    serie = []
    labels = []
    for idx,dummy in enumerate(parse):
        serie.append(dummy)
        labels.append(str(idx)+'h')

    return JsonResponse(
            data={'series': [serie], 'labels': labels})

def payment_season_day(request):
    payments = Payment.objects.all()
    #Computing the nb of payments per week
    parse = [0] * 7
    for pay in payments:
        parse[pay.date.weekday()-1] += 1
    #Format
    serie = []
    labels = ['Monday','Tuesday','Wednesday','Thursday'
            ,'Friday','Saturday','Sunday']
    for idx,dummy in enumerate(parse):
        serie.append(dummy)

    return JsonResponse(
            data={'series': [serie], 'labels': labels})

def payment_volume_weekly(request):
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    last_monday = today - datetime.timedelta(0
            ,today.hour*60*60+today.minute*60+today.second,0)
    while last_monday.weekday() != 0:
        last_monday -= datetime.timedelta(1,0,0)
    date_start = last_monday - datetime.timedelta(7*51,0,0)
    payments = Payment.objects.filter(date__gt = date_start)
    #Computing the nb of payments per week
    parse = [0] * 52
    for pay in payments:
        index = int((pay.date - date_start).days/7)
        parse[index] += pay.amount
    #Format
    serie = []
    labels = []
    dates = []
    for idx,dummy in enumerate(parse):
        serie.append(dummy)
        dates.append(date_start + datetime.timedelta((idx+1)*7,0,0))
        if idx == 0:
            labels.append(str(dates[idx].month) + '/' + str(dates[idx].year))
        elif dates[idx].month != dates[idx-1].month:
            labels.append(str(dates[idx].month) + '/' + str(dates[idx].year))
        else:
            labels.append('')

    return JsonResponse(
            data={'series': [serie], 'labels': labels})

def payment_number_weekly(request):
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    last_monday = today - datetime.timedelta(0
            ,today.hour*60*60+today.minute*60+today.second,0)
    while last_monday.weekday() != 0:
        last_monday -= datetime.timedelta(1,0,0)
    date_start = last_monday - datetime.timedelta(7*51,0,0)
    payments = Payment.objects.filter(date__gt = date_start)
    #Computing the nb of payments per week
    parse = [0] * 52
    for pay in payments:
        index = int((pay.date - date_start).days/7)
        parse[index] += 1
    #Format
    serie = []
    labels = []
    dates = []
    for idx,dummy in enumerate(parse):
        serie.append(dummy)
        dates.append(date_start + datetime.timedelta((idx+1)*7,0,0))
        if idx == 0:
            labels.append(str(dates[idx].month) + '/' + str(dates[idx].year))
        elif dates[idx].month != dates[idx-1].month:
            labels.append(str(dates[idx].month) + '/' + str(dates[idx].year))
        else: labels.append('')

    return JsonResponse(
            data={'series': [serie], 'labels': labels})

def account_new_week(request):
    # Grabbing accounts in the relevant period
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    last_monday = today - datetime.timedelta(0
            ,today.hour*60*60+today.minute*60+today.second,0)
    while last_monday.weekday() != 0:
        last_monday -= datetime.timedelta(1,0,0)
    date_start = last_monday - datetime.timedelta(7*51,0,0)
    accounts_ecos = Account.objects.filter(reg_date__gt = date_start,
            plan_product__name = 'Sunking Eco')
    accounts_pros = Account.objects.filter(reg_date__gt = date_start,
            plan_product__name = 'Sunking Pro')
    accounts_shs = Account.objects.filter(reg_date__gt = date_start,
            plan_product__name = 'Sunking Home')

    # Computing the nb of payments per week
    parse_eco = [0] * 52
    parse_pro = [0] * 52
    parse_shs = [0] * 52
    week = datetime.timedelta(7,0,0)
    week_start = date_start
    week_end = date_start + week
    labels = []
    for i in range(0,52):
        parse_eco[i] = accounts_ecos.new(week_start,week_end).count()
        parse_pro[i] = accounts_pros.new(week_start,week_end).count()
        parse_shs[i] = accounts_shs.new(week_start,week_end).count()
        if i == 0:
            labels.append(str(week_end.month) + '/' + str(week_end.year))
        elif week_end.month != week_start.month:
            labels.append(str(week_end.month) + '/' + str(week_end.year))
        else: labels.append('')
        week_start = week_end
        week_end = week_start + week

    return JsonResponse(
            data={'series': [parse_eco,parse_pro,parse_shs], 'labels': labels})

def account_number_by_disable(request):
    accounts = Account.objects.all().active
    serie_e = [0] * 51
    serie_d = [0] * 51
    for acc in accounts:
        index = int(min(50,max(0,acc.days_credit*(-1)+25)))
        if index >= 25: serie_e[index] += 1
        else: serie_d[index] += 1

    #Format
    labels = []
    for idx,dummy in enumerate(serie_e):
        if idx == 0: labels.append('-25(+)')
        elif idx == 50: labels.append('25(+)')
        else: labels.append(str(idx-25))

    return JsonResponse(
            data={'series': [serie_e,serie_d], 'labels': labels})

def account_outstanding_by_disable(request):
    accounts = Account.objects.all().active
    serie_e = [0] * 51
    serie_d = [0] * 51
    for acc in accounts:
        index = int(min(50,max(0,acc.days_credit*(-1)+25)))
        if index >= 25: serie_e[index] += acc.left_to_pay
        else: serie_d[index] += acc.left_to_pay

    #Format
    labels = []
    for idx,dummy in enumerate(serie_e):
        if idx == 0: labels.append('-25(+)')
        elif idx == 50: labels.append('25(+)')
        else: labels.append(str(idx-25))

    return JsonResponse(
            data={'series': [serie_e,serie_d], 'labels': labels})

#***************************************************************
#******************** CUSTOM FUNCTIONS *************************
#***************************************************************

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
