from django.shortcuts import render, get_object_or_404
from django.http import Http404

def index(request):
    context = {}
    return render(request, 'base.html', context)
