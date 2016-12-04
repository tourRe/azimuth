from django.shortcuts import render
from system.tasks import fetch_data

def collect(request, option=""):
    fetch_data(option)
