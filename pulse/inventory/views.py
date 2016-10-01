import datetime
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Warehouse, InventoryItem, Product, Transaction, TransactionItem

def index(request):
    warehouse_list = Warehouse.objects.order_by('name')
    products_list = Product.objects.all()
    # creating a dict with the values for index display
    invItem_listAll = {}
    for w in warehouse_list:
        invItem_listAll[w.name] = []
        for p in products_list:
            invItem_listAll[w.name].append(w.qty(p))
    # defining context to be used in the template
    context = {
            'warehouse_list': warehouse_list,
            'invItem_listAll': invItem_listAll,
            'products_list': products_list,
            }
    return render(request, 'inventory/index.html', context)

def warehouse(request, warehouse_name):
    warehouse = get_object_or_404(Warehouse, name=warehouse_name)
    warehouse_list = Warehouse.objects.order_by('name')
    invItem_list = InventoryItem.objects.filter(warehouse=warehouse)
    context = {'warehouse_list': warehouse_list,
            'warehouse': warehouse, 
            'invItem_list': invItem_list}
    return render(request, 'inventory/warehouse.html',context) 

# HANDLES TRANSACTION FORMS ON WAREHOUSE PAGE
def confirmation(request, warehouse_name):
    
    # Grabbing transaction parameters based on form variables
    w_from = get_object_or_404(Warehouse, name=warehouse_name)
    w_to = Warehouse.objects.get(name=request.POST['destination'])
    p = Product.objects.get(name=request.POST['product'])
    item_from = InventoryItem.objects.get(
            warehouse=w_from,
            product=p)
    if w_from.name == '_Client':
        ttype = 2
    elif w_from.name == '_Supplier':
        ttype = 1
    else:
        ttype = 4
    
    # Defining the transaction and transaction item
    transaction = Transaction.objects.create(
            transaction_type = ttype, 
            date = datetime.datetime.today(), 
            origin = w_from,
            destination = w_to,
            comment = 'test_transaction')
    transItem = TransactionItem(
            transaction = transaction,
            item = item_from,
            qty = int(request.POST['qty']))
    
    # Preparing context to return to the warehouse page
    warehouse_list = Warehouse.objects.order_by('name')
    invItem_list = InventoryItem.objects.filter(warehouse=w_from)
    context = {'warehouse_list': warehouse_list,
        'warehouse': w_from,
        'invItem_list': invItem_list,
        }
    
    # Testing transItem for save, returning an error if necessary
    try:
        transItem.save()
    except ValidationError as e:
        context['error_message'] = next (iter (e.message_dict.values()))
        transaction.delete()
        return render(request, 'inventory/warehouse.html', context)
    context['error_message'] = "Your transfer was successfully applied"
    return render(request, 'inventory/warehouse.html', context)
