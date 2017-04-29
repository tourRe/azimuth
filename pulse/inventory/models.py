from django.db import models
# Imports to receive the pre_delete signal and revert transaction in inventory
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
# Time packages for dates with timezone management
import datetime, pytz
# Could import specific models only but it creates circular import error
import sales

# SIMPLE WAREHOUSE CLASS
# Would ideally initiate an inventory item for each product upon creation
class Warehouse(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    # Returns the qty of given 'product' in inventory
    def qty(self,product):
        try:
            item=InventoryItem.objects.get(
                    warehouse=self,
                    product=product)
        except:
            return 0
        return item.qty

@receiver(post_save, sender=Warehouse, 
        dispatch_uid='Warehouse_postsave_signal')
def initiate_warehouse(sender, instance, created, *args, **kwargs):
    if created:
        prods = Product.objects.all()
        for prod in prods:
            InventoryItem.objects.create(product=prod,warehouse=instance)

# SIMPLE PRODUCTS CLASS, INCLUDING POWER
class Product(models.Model):
    name = models.CharField(max_length=30)
    brand = models.CharField(max_length=30, null=True)
    power = models.FloatField(default=0, null=True)
    label = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name

# ITEM IN INVENTORY, COULD BE REPLACED BY FIELDS IN EACH WAREHOUSE
class InventoryItem(models.Model):
    product = models.ForeignKey(Product)
    warehouse = models.ForeignKey(Warehouse)
    qty = models.IntegerField(default=0)

    def __str__(self):
        return ('%s in %s: %s' 
                % (str(self.product), str(self.warehouse), str(self.qty)))

    # Returns the number of units sold in the last 'days'
    # Could include other transaction types at some point?
    def get_sold(self,days):
        result = 0
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        from_date = today - datetime.timedelta(days,0,0)
        agents = sales.models.Agent.objects.filter(warehouse = self.warehouse)
        return sales.models.Account.objects.filter(
                agent__in = agents, reg_date__gte = from_date,
                plan_product=self.product).count()

    # Returns the list of sales in the last 7, 14 and 30 days
    # Designed for the individual warehouse view
    @property
    def get_sold_sample(self):
        return [self.get_sold(7),self.get_sold(14),self.get_sold(30)]
 
    # Returns the inventory days based on last 14 days of sales
    # Designed for the inventory index view
    @property
    def get_invDays_14(self):
        result = 0
        sold = self.get_sold(14)
        if sold == 0:
            return -1
        return self.qty/(sold/14)

# TRANSACTION CLASS WHICH CAN CONTAIN SEVERAL TRANSACTION ITEMS
# Although it's never the case at this point...
# Also need to look into what to do with "types", not really useful yet
# Could probably add a user in the class
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
    account = models.ForeignKey('sales.Account', 
            null=True, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
                return "from %s to %s (%s)" % (self.origin, self.destination,
                        self.comment)

# TRANSACTION ITEM FOR A GIVEN PRODUCT
class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem)
    qty = models.PositiveIntegerField(default=0)

    # Overrides the Django clean function to refuse certain transactions
    def clean(self):
        # transactions with a qty of 0 not allowed
        if self.qty == 0:
            raise ValidationError(_(
                'Error: No quantity selected'))

    # Overrides the Django save function to update inventory items on save
    # Also calls to clean function through "full_clean()"
    def save(self, *args, **kwargs):
        self.full_clean()
        w_from = self.transaction.origin
        w_to = self.transaction.destination
        item_to, created = InventoryItem.objects.get_or_create(
                warehouse = w_to, product = self.item.product)
        # doesn't update _Client quantity on sales
        if w_to.name != "_Client":
            item_to.qty += self.qty
        item_to.save()
        # doesn't update _Supplier quantity on product reception
        if w_from.name != "_Supplier":
            self.item.qty -= self.qty
        self.item.save()
        # calls the actual Django save function
        super(TransactionItem, self).save(*args, **kwargs)

    def __str__(self):
                return "%s %s(s) from %s to %s" % (self.qty, 
                        self.item.product, self.transaction.origin,
                        self.transaction.destination)

# Removes quantities in inventory items on transaction item delete
# Has to use the 'delete_signal' for mass deletes
# Mirrors the actions performed on save
@receiver(pre_delete, sender=TransactionItem, 
        dispatch_uid='TransactionItem_delete_signal')
def reverse_transactions(sender, instance, using, **kwargs):
    w_from = instance.transaction.origin
    w_to = instance.transaction.destination
    item_to = InventoryItem.objects.get(
            warehouse= w_to, product = instance.item.product)
    if w_to.name != "_Client":
        item_to.qty -= instance.qty
    item_to.save()
    if w_from.name != "_Supplier":
        instance.item.qty += instance.qty
    instance.item.save()
