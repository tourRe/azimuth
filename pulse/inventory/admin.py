from django.contrib import admin
from .models import (Warehouse, Product, InventoryItem)

# Register your models here.

admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(InventoryItem)
