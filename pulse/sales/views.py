from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'sales/index.html', context)
