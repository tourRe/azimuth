from django.db import models
from inventory.models import Product

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')))
    phone = models.CharField(max_length=16)
    location = models.CharField(max_length=30)

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
            choices=(('M', 'Male'),('F', 'Female')))
    location = models.CharField(max_length=30)
    phone = models.CharField(max_length=16)
    manager = models.ForeignKey(Manager)

    def __str__(self):
        return ('%s %s (%s)' % (self.firstname, self.lastname, self.location))

class Plan(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300, blank=True, null=True)
    product = models.ForeignKey(Product)
    upfront = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    weekly = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Account(models.Model):
    account_GLP = models.CharField(max_length=7)
    account_Angaza = models.CharField(max_length=8)
    client = models.ForeignKey(Client)
    plan = models.ForeignKey(Plan)
    reg_date = models.DateTimeField('registration date')
    agent = models.ForeignKey(Agent)

    def __str__(self):
        return self.account_GLP

    def paid(self):
        payments = Payment.objects.get(account = self)
        results = 0
        for payment in payments:
            results += payment.amount
        return results

class Payment(models.Model):
    account = models.ForeignKey(Account)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    agent = models.ForeignKey(Agent)

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))
