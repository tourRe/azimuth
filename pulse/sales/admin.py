from django.contrib import admin
from .models import (Manager, Agent, Plan, Payment, Account, Client)

# Register your models here.
admin.site.register(Manager)
admin.site.register(Agent)
admin.site.register(Plan)
admin.site.register(Account)
admin.site.register(Payment)
admin.site.register(Client)
