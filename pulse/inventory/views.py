from django.shortcuts import render, get_object_or_404
from django.http import Http404
# Can be removed once all the views are changed and render fction is used
from django.http import HttpResponse
# Can be removed once all the views are changed and render fction is used
from django.template import loader
from .models import Warehouse, InventoryItem, Product

# Create your views here.
def index(request):
    warehouse_list = Warehouse.objects.all()
    template = loader.get_template('inventory/index.html')
    context = {
            'warehouse_list': warehouse_list,
            }
    return render(request, 'inventory/index.html', context)

def warehouse(request, warehouse_name):
    warehouse = get_object_or_404(Warehouse, name=warehouse_name)
    warehouse_list = Warehouse.objects.all()
    invItem_list = InventoryItem.objects.filter(warehouse=warehouse)
    context = {'warehouse': warehouse, 
            'warehouse_list': warehouse_list,
            'invItem_list': invItem_list}
    return render(request, 'inventory/warehouse.html',context) 

def transaction(request, warehouse_id):
    return HttpResponse("You're performing a transaction from warehouse %s"
            % warehouse_id)
