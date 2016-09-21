from django.contrib import admin
from .models import (Manager, Agent, Plan)

# Register your models here.
admin.site.register(Manager)
admin.site.register(Agent)
admin.site.register(Plan)
