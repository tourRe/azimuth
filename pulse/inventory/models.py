from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
    def qty(self,product):
        try:
            item=InventoryItem.objects.get(
                    warehouse=self,
                    product=product)
        except:
            return 0
        return item.qty

class Product(models.Model):
    name = models.CharField(max_length=30)
    brand = models.CharField(max_length=30)
    power = models.FloatField(default=0)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    product = models.ForeignKey(Product)
    warehouse = models.ForeignKey(Warehouse)
    qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return ('%s in %s: %s' 
                % (str(self.product), str(self.warehouse), str(self.qty)))

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
    origin = models.ForeignKey(Warehouse, related_name='origin')
    destination = models.ForeignKey(Warehouse, related_name='destination')
    comment = models.CharField(max_length=255, blank=True, null=True)
    # need to add a user for the transaction

    def __str__(self):
                return "%s on %s" % (self.transaction_type, 
                        str(self.date))

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction)
    item = models.ForeignKey(InventoryItem)
    qty = models.PositiveIntegerField(default=0)
