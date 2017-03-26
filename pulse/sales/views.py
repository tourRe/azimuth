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

# ****************************************************************
# ********************** GLOBAL VARIABLES ************************
# ****************************************************************

today = datetime.datetime.today().replace(tzinfo=pytz.utc)

# Calculating labels for weekly graphs

last_monday = today - datetime.timedelta(0
        ,today.hour*60*60+today.minute*60+today.second,0)
while last_monday.weekday() != 0:
    last_monday -= datetime.timedelta(1,0,0)

last_friday = today - datetime.timedelta(0
        ,today.hour*60*60+today.minute*60+today.second,0)
while last_friday.weekday() != 4:
    last_friday -= datetime.timedelta(1,0,0)

date_start = last_monday - datetime.timedelta(7*51,0,0)
labels_weekly = []
dates = []
for idx in range(0,52):
    dates.append(date_start + datetime.timedelta((idx+1)*7,0,0))
    if idx == 0:
        labels_weekly.append(str(dates[idx].month) + '/' + str(dates[idx].year))
    elif dates[idx].month != dates[idx-1].month:
        labels_weekly.append(str(dates[idx].month) + '/' + str(dates[idx].year))
    else:
        labels_weekly.append('')

# ****************************************************************
# ************************ MENU CONTEXT **************************
# ****************************************************************

context = {}
all_agents = Agent.objects.exclude(category = 'H').order_by('location')
context['all_agents'] = all_agents
all_managers = Manager.objects.order_by('firstname')
context['all_managers'] = all_managers 

# ****************************************************************
# **************************** VIEWS *****************************
# ****************************************************************

def index(request):
    # Preparing tables
    context['all_clients'] = Client.objects.all()
    context['all_accounts'] = Account.objects.all()
    context['all_payments'] = Payment.objects.all()

    return render(request, 'sales/index.html', context)

def managers(request):
    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    for manager in all_managers:
        key = ("<a href='/sales/managers/" + manager.firstname + "/'>"
                + " " + manager.firstname + " " + manager.lastname + "</a>")
        agents = Agent.objects.filter(manager = manager)
        account_table[key] = Account.objects.filter(agent__in = agents)
    context['account_table'] = account_table
    return render(request, 'sales/managers.html', context)

def manager(request, manager_firstname):
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

def agents(request):
    # Preparing table for account_sets display
    account_table = collections.OrderedDict()
    sales_table = collections.OrderedDict()
    com_table = collections.OrderedDict()
    for agent in all_agents:

        key = ("<a href='/sales/agents/" + agent.login + "/'>"
                + " " + agent.location+ "</a>")
        accs = agent.accounts
        account_table[key] = accs

        sales = []
        for idx in range(0,9):
            sales.append(agent.sales_week(idx))
        sales_table[key] = sales

        com = []
        for idx in range(0,9):
            com.append(agent.com_week(idx))
        com_table[key] = com

    context['account_table'] = account_table
    context['sales_table'] = sales_table
    context['com_table'] = com_table
    return render(request, 'sales/agents.html', context)

def agent(request, agent_login):
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
    par7_table = {}
    for acc in accounts.at_risk(7,0):
        key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                + " " + acc.account_GLP + " (" + acc.account_Angaza 
                + ")</a>")
        par7_table[key] = acc
    context['par7_table'] = par7_table

    # Adding PDP14 table to context
    pdp14_table = {}
    for acc in accounts.delayed_payment(14,0):
        key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                + " " + acc.account_GLP + " (" + acc.account_Angaza 
                + ")</a>")
        pdp14_table[key] = acc
    context['pdp14_table'] = pdp14_table

    # Adding PDP14 table to context
    pdp30_table = {}
    for acc in accounts.delayed_payment(30,0):
        key = ("<a href='/sales/accounts/" + acc.account_Angaza + "/'>"
                + " " + acc.account_GLP + " (" + acc.account_Angaza 
                + ")</a>")
        pdp30_table[key] = acc
    context['pdp30_table'] = pdp30_table

    return render(request, 'sales/agent.html', context)

def clients(request):
    return render(request, 'sales/clients.html', context)

def client(request, client_pk):
    client = Client.objects.get(pk = client_pk)
    context['client'] = client

    # Adding table with client for summary display
    the_client = collections.OrderedDict()
    key = ("<a href='/sales/clients/" + client_pk + "/'>"
            + client.name +"</a>")
    the_client[key] = client
    context['the_client'] = the_client

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

def accounts(request):
    # Sending accounts and payments to context
    context['accounts'] = Account.objects.all()
    context['payments'] = Payment.objects.all()

    # table_1['... of which unlocked'] = str("{:,}".format(
    #         Account.objects.filter(status='u').count()))
    # table_1['... of which enabled'] = str("{:,}".format(
    #         Account.objects.filter(status='e').count()))
    # table_1['... of which disabled'] = str("{:,}".format(
    #         Account.objects.filter(status='d').count()))
    # table_1['... of which written off'] = str("{:,}".format(
    #         Account.objects.filter(status='w').count()))
    # table_1['Repayment ratio (CRR)'] = ratio(paid,paid_expected,pc=True)
    # table_1['Number of payments'] = str("{:,}".format(pay_number))
    # table_1['Average payment (SLL)'] = ratio(paid,pay_number)
    # table_1['PAR (14 days)'] = ratio(oar_14,outstanding,pc=True,dec=2)
    # table_1['Average days disabled'] = ratio(days_disabled,account_number)
    # table_1['Average unit price (SLL)'] = ratio(paid+outstanding,account_number)

    return render(request, 'sales/accounts.html', context)

def account(request, account_Angaza):
    account = Account.objects.get(account_Angaza = account_Angaza)
    context['account'] = account
    return render(request, 'sales/account.html', context)

def payments(request):
    return render(request, 'sales/payments.html', context)

# ****************************************************************
# *************************** REPORTS ****************************
# ****************************************************************

def reports_revenue(request):
    accounts = Account.objects.all().new_LM
    rev_table = collections.OrderedDict()
    for a in accounts.values('plan_name').order_by('plan_name').distinct():
        name = a['plan_name']
        rev_table[name] = accounts.filter(plan_name = name)
    rev_table['TOTAL'] = accounts
    context['rev_table'] = rev_table
    return render(request, 'sales/reports_revenue.html', context)

def reports_AR(request):
    accounts = Account.objects.all().active_LM
    AR_table = collections.OrderedDict()
    for a in accounts.values('plan_name').order_by('plan_name').distinct():
        name = a['plan_name']
        AR_table[name] = accounts.filter(plan_name = name)
    AR_table['TOTAL'] = accounts
    context['AR_table'] = AR_table
    return render(request, 'sales/reports_AR.html', context)

def reports_com(request):
    agent_list = Agent.objects.order_by('location')
    real_agents = agent_list.exclude(login = 'hq.demo')
    real_agents = real_agents.exclude(login = 'hq.marketing')
    accounts = Account.objects.all().active_LM
    com_table = collections.OrderedDict()
    com_table['Payment plan'] = []
    for agent in real_agents:
        com_table['Payment plan'].append(agent.login)
    for a in accounts.values('plan_name').order_by('plan_name').distinct():
        name = a['plan_name']
        com_table[name] = []
        for agent in real_agents:
            com_table[name].append(
                    accounts.filter(plan_name = name, agent = agent).unlocked_LM.nb)
    com_table['TOTAL'] = []
    for agent in real_agents:
        com_table['TOTAL'].append(
                accounts.filter(agent = agent).unlocked_LM.nb)
    context['com_table'] = com_table
    return render(request, 'sales/reports_com.html', context)

# ***************************************************************
# ************************* GRAPHS ******************************
# ***************************************************************

def payment_season_hour(request):
    payments = Payment.objects.all()
    #Computing the nb of payments per hour of the day
    serie = [0] * 24
    for pay in payments: serie[pay.date.hour] += 1
    #Labels
    labels = []
    for idx in range(0,24): labels.append(str(idx)+'h')
    #Returning Graph
    return JsonResponse(data={'series': [serie], 'labels': labels})

def payment_season_day(request):
    payments = Payment.objects.all()
    #Computing the nb of payments per day of the week
    serie = [0] * 7
    for pay in payments: serie[pay.date.weekday()-1] += 1
    #Labels
    labels = ['Monday','Tuesday','Wednesday','Thursday',
            'Friday','Saturday','Sunday']
    #Returning Graph
    return JsonResponse(data={'series': [serie], 'labels': labels})

def payment_volume_weekly(request, agent=None):
    payments = Payment.objects.filter(date__gt = date_start)
    if not agent: pass
    else:
        this_agent = Agent.objects.get(login=agent)
        payments = payments.filter(account__agent = this_agent)
    #Computing the nb of payments per week
    serie_down = [0] * 52
    serie_inst = [0] * 52
    for pay in payments:
        index = int((pay.date - date_start).days/7)
        if pay.is_upfront: serie_down[index] += pay.amount
        else: serie_inst[index] += pay.amount
    #Returning Graph
    return JsonResponse(
            data={'series': [serie_inst,serie_down], 'labels': labels_weekly})

def payment_number_weekly(request, agent=None):
    payments = Payment.objects.filter(date__gt = date_start)
    if not agent: pass
    else:
        this_agent = Agent.objects.get(login=agent)
        payments = payments.filter(account__agent = this_agent)
    #Computing the volume of payments per week
    serie_down = [0] * 52
    serie_inst = [0] * 52
    for pay in payments: 
        index = int((pay.date - date_start).days/7)
        if pay.is_upfront: serie_down[index] += 1
        else: serie_inst[index] += 1
    #Returning Graph
    return JsonResponse(
            data={'series': [serie_inst,serie_down], 'labels': labels_weekly})

def account_new_week(request, agent=None):
    # Grabbing accounts in the relevant period
    accounts = Account.objects.filter(reg_date__gt = date_start)
    if not agent: pass
    else:
        this_agent = Agent.objects.get(login=agent)
        accounts = accounts.filter(agent = this_agent)
    accounts_ecos = accounts.filter(plan_product__name = 'Eco EB')
    accounts_pros = accounts.filter(plan_product__name = 'Pro EB')
    accounts_shs = accounts.filter(plan_product__name = 'Home EB')
    # Computing the nb of accounts creation per week
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
        week_start = week_end
        week_end = week_start + week
    #Returning Graph
    return JsonResponse(data={'series': [parse_eco,parse_pro,parse_shs],
        'labels': labels_weekly})

def revenue_new_week(request, agent=None):
    # Grabbing accounts in the relevant period
    accounts = Account.objects.filter(reg_date__gt = date_start)
    if not agent: pass
    else:
        this_agent = Agent.objects.get(login=agent)
        accounts = accounts.filter(agent = this_agent)
    accounts_ecos = accounts.filter(plan_product__name = 'Eco EB')
    accounts_pros = accounts.filter(plan_product__name = 'Pro EB')
    accounts_shs = accounts.filter(plan_product__name = 'Home EB')
    # Computing the nb of accounts creation per week
    parse_eco = [0] * 52
    parse_pro = [0] * 52
    parse_shs = [0] * 52
    week = datetime.timedelta(7,0,0)
    week_start = date_start
    week_end = date_start + week
    labels = []
    for i in range(0,52):
        parse_eco[i] = accounts_ecos.new(week_start,week_end).plan_tot
        parse_pro[i] = accounts_pros.new(week_start,week_end).plan_tot
        parse_shs[i] = accounts_shs.new(week_start,week_end).plan_tot
        week_start = week_end
        week_end = week_start + week
    #Returning Graph
    return JsonResponse(data={'series': [parse_eco,parse_pro,parse_shs],
        'labels': labels_weekly})

def account_number_by_disable(request, agent=None):
    accounts = Account.objects.all().active
    if not agent: pass
    else: 
        this_agent = Agent.objects.get(login=agent)
        accounts = accounts.filter(agent = this_agent)
    serie_e = [0] * 51
    serie_d = [0] * 51
    for acc in accounts:
        index = int(min(50,max(0,acc.credit_relative+25)))
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

def account_outstanding_by_disable(request, agent=None):
    accounts = Account.objects.all().active
    if not agent: pass
    else: 
        this_agent = Agent.objects.get(login=agent)
        accounts = accounts.filter(agent = this_agent)
    serie_e = [0] * 51
    serie_d = [0] * 51
    for acc in accounts:
        index = int(min(50,max(0,acc.credit_relative+25)))
        if index >= 25: serie_e[index] += acc.outstanding
        else: serie_d[index] += acc.outstanding

    #Format
    labels = []
    for idx,dummy in enumerate(serie_e):
        if idx == 0: labels.append('-25(+)')
        elif idx == 50: labels.append('25(+)')
        else: labels.append(str(idx-25))

    return JsonResponse(
            data={'series': [serie_e,serie_d], 'labels': labels})

# ***************************************************************
# ******************** CUSTOM FUNCTIONS *************************
# ***************************************************************

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
