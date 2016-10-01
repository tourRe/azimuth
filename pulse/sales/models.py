import datetime

from django.db import models
from inventory.models import Product

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    phone = models.CharField(max_length=16, null=True)
    location = models.CharField(max_length=30, null=True)

    def __str__(self):
        return ('%s (%s)' % (self.name, self.location))

class Manager(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    start_date = models.DateTimeField('date hired')
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')))
    district = models.CharField(max_length=30)
    phone = models.CharField(max_length=16)

    def __str__(self):
        return ('%s %s (%s)' % (self.firstname, self.lastname, self.district))

class Agent(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    start_date = models.DateTimeField('date hired')
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    location = models.CharField(max_length=30)
    phone = models.CharField(max_length=16)
    manager = models.ForeignKey(Manager)
    label = models.CharField(max_length=50, null=True)

    def __str__(self):
        return ('%s %s (%s)' % (self.firstname, self.lastname, self.location))

class Account(models.Model):
    STATUS = (('e', 'Active'), ('d', 'Deactivated'), 
            ('u', 'Unlocked'), ('w', 'Written Off'))

    account_Angaza = models.CharField(max_length=8)
    account_GLP = models.CharField(max_length=7)
    client = models.ForeignKey(Client)
    plan_name = models.CharField(max_length=40)
    plan_product = models.ForeignKey(Product)
    plan_up = models.PositiveIntegerField(default=0)
    plan_tot = models.PositiveIntegerField(default=0)
    plan_week = models.PositiveIntegerField(default=0)
    reg_date = models.DateTimeField('registration date')
    agent = models.ForeignKey(Agent)
    status = models.CharField(max_length=1,choices=STATUS)

    def __str__(self):
        return '%s (%s)' % (self.account_GLP, self.plan_name)

    def paid(self):
        results = 0
        for payment in Payment.objects.filter(account = self):
            results+=payment.amount
        return results

    def paid_thisMonth(self):
        results = 0
        today = datetime.datetime.today()
        for payment in Payment.objects.filter(account = self, 
                date__year = today.year, date__month = today.month):
            results += payment.amount
            print('youpi')
        return results
    
class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    agent = models.ForeignKey(Agent)

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))
