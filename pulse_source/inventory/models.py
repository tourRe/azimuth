from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=30)
    brand = models.CharField(max_length=30)
    power = models.FloatField(default=0)
    
    def __str__(self):
        return self.name

class StockStatus(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.name
    
    class Meta():
        verbose_name_plural = 'Stock Status'

class InventoryItem(models.Model):
    item_type = models.ForeignKey(Product)
    storage = models.ForeignKey(Warehouse)
    status = models.ForeignKey(StockStatus)
    qty = models.PositiveIntegerField(default=0)

    def __str(self):
        return ('%s %s in %s' 
                % (str(self.qty), str(self.item_type), str(self.storage)))

class Transaction(models.Model):
    TYPE_RECEIVED = 1
    TYPE_SOLD = 2
    TYPE_RETURNED = 3
    TYPE_INTERNAL = 4

    TYPE_CHOICES = (
        (TYPE_RECEIVED, 'Received'),
        (TYPE_SOLD, 'Sold'),
        (TYPE_RETURNED, 'Returned to Stock'),
        (TYPE_INTERNAL, 'Internal Transfer'),
        )

    transaction_type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    # need to add a user for the transaction

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction)
    item = models.ForeignKey(InventoryItem)
    qty = models.PositiveIntegerField(default=0)
