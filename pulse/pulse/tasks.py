# Tasks file for celery
from celery import task
from sales.models import Client

@task(name="sum of two numbers")
def add(x, y):
        return x + y

@task
def collect(x, y):
        return x + y
