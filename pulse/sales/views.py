from django.shortcuts import render
from .models import Agent, Manager

def index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/index.html', context)

def manager_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/manager_index.html', context)

def manager(request, manager_firstname):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/manager.html', context)

def agent_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/agent_index.html', context)

def agent(request, agent_login):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/agent.html', context)

def client_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/client_index.html', context)

def client(request, client_pk):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/client.html', context)

def account_index(request):
    agent_list = Agent.objects.order_by('location')
    manager_list = Manager.objects.order_by('firstname')
    context = {
            'manager_list' : manager_list,
            'agent_list' : agent_list
            }
    return render(request, 'sales/account_index.html', context)

def account(request, account_Angaza):
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
