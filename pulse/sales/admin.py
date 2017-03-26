from django.contrib import admin
from .models import (Manager, Agent, Payment, Account, Client, ComPlan)

# Register your models here.
admin.site.register(Manager)
admin.site.register(Agent)
admin.site.register(Account)
admin.site.register(Payment)
admin.site.register(Client)
admin.site.register(ComPlan)
