import datetime
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

def confirmation(request, warehouse_name):
    # Defining transaction parameters based on form variables
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
    transaction = Transaction.objects.create(
            transaction_type = ttype, 
            date = datetime.datetime.today(), 
            comment = 'test_transaction',
            origin = w_from,
            destination = w_to)
    transItem = TransactionItem.objects.create(
            transaction = transaction,
            item = item_from,
            qty = int(request.POST['qty']))
    if transItem.qty > item_from.qty:
        warehouse_list = Warehouse.objects.order_by('name')
        invItem_list = InventoryItem.objects.filter(warehouse=warehouse_from)
        return render(request, 'inventory/warehouse.html', {
            'warehouse_list': warehouse_list,
            'warehouse': w_from,
            'invItem_list': invItem_list,
            'error_message':'Not enough products to perform that transfer',
            })
    elif transItem.qty == 0:
        warehouse_list = Warehouse.objects.order_by('name')
        invItem_list = InventoryItem.objects.filter(warehouse=warehouse_from)
        return render(request, 'inventory/warehouse.html', {
            'warehouse_list': warehouse_list,
            'warehouse': w_from,
            'invItem_list': invItem_list,
            'error_message':'No quantity selected',
            })
    else:
        transaction.save()
        transItem.save()
        if w_from.name != '_Supplier':
            item_from.qty -= transItem.qty
            item_from.save()
        item_to, created = InventoryItem.objects.get_or_create(
                warehouse=w_to, product=p)
        item_to.qty += transItem.qty
        item_to.save()
        context = {}
        return render(request, 'inventory/confirmation.html', context)
