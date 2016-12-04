from django.shortcuts import render, get_object_or_404
from django.http import Http404
from system.models import Update

updates = Update.objects.all()
last_update = updates.last_update()
last_full_update = updates.last_full_update()

context = {}
context['last_update'] = last_update
context['last_full_update'] = last_full_update

def index(request):
    return render(request, 'index.html', context)
