import datetime
import calendar
import pytz

from django.db import models
from inventory.models import Product, Warehouse

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
    warehouse = models.ForeignKey(Warehouse)
    phone = models.CharField(max_length=16)
    manager = models.ForeignKey(Manager)
    login = models.CharField(max_length=30, null=True)
    label = models.CharField(max_length=50, null=True)

    def __str__(self):
        return ('%s (%s %s)' % (self.location, self.firstname, self.lastname))

class Account(models.Model):
    STATUS = (('e', 'Active'), ('d', 'Deactivated'), 
            ('u', 'Unlocked'), ('w', 'Written Off'))

    account_Angaza = models.CharField(max_length=8)
    account_GLP = models.CharField(max_length=7)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=40)
    plan_product = models.ForeignKey(Product)
    plan_up = models.PositiveIntegerField(default=0)
    plan_tot = models.PositiveIntegerField(default=0)
    plan_week = models.PositiveIntegerField(default=0)
    reg_date = models.DateTimeField('registration date')
    agent = models.ForeignKey(Agent)
    status = models.CharField(max_length=1,choices=STATUS)

    def __str__(self):
        return '%s - %s' % (self.account_GLP, self.plan_name)

    def paid(self):
        result = 0
        for payment in Payment.objects.filter(account = self):
            result += payment.amount
        return result

    def paid_thisMonth(self, offset):
        result = 0
        today = datetime.datetime.today()
        _today = add_months(today,offset).replace(tzinfo=pytz.utc)
        for payment in Payment.objects.filter(account = self): 
            if (payment.date.year == _today.year and 
                    payment.date.month == _today.month):
                results += payment.amount
        return result

    def pay_number(self):
        return Payment.objects.filter(account = self).count()

    def pay_number_thisMonth(self, offset):
        result = 0
        today = datetime.datetime.today()
        _today = add_months(today,offset).replace(tzinfo=pytz.utc)
        for payment in Payment.objects.filter(account = self): 
            if (payment.date.year == _today.year and 
                    payment.date.month == _today.month):
                result += 1
        return result

    def paid_expected(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        delta = today - self.reg_date
        full_weeks = int(toWeeks(delta))
        return min(self.plan_up + self.plan_week*full_weeks, 
                self.plan_tot)

    def paid_expected_eom(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eom = monthEnd(today)
        delta = eom - self.reg_date
        full_weeks = int(toWeeks(delta))
        return min(self.plan_up + self.plan_week*full_weeks, 
                self.plan_tot)

    def payment_deficit(self):
        return self.paid() - self.paid_expected()

    def payment_deficit_eom(self):
        return self.paid_thisMonth(0) - self.paid_expected_eom()

    def lastPay(self):
        r = list(Payment.objects.filter(account = self).order_by('date')[:1])
        if r:
            return r[0]
        return None

    # Total numbers of days disabled. Returns the current disabled if now = True
    def days_disabled(self, now = False):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        result = 0
        for idx, payment in enumerate(
                Payment.objects.filter(account = self).order_by('date')):
            if idx == 0:
                weeks_credit = ((payment.amount - self.plan_up)/self.plan_week 
                        + 1)
                disable_date = (payment.date 
                        + datetime.timedelta(weeks_credit*7,0,0))
            else:
                result += max(toWeeks(payment.date - disable_date)*7,0)
                weeks_credit = payment.amount / self.plan_week
                disable_date = (max(disable_date, payment.date) 
                        + datetime.timedelta(weeks_credit*7,0,0))
            prev_pay = payment
        if now:
            result = 0
        if self.status != 'u':
            result += max(0,toWeeks(today - disable_date)*7)
        return result

    # Returns outstanding amount for which no payments in the last 'days'
    def OAR(self,days):
        if self.days_disabled(now=True) > days:
            return self.plan_tot - self.paid()
        return 0

class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    agent = models.ForeignKey(Agent)
    id_Angaza = models.CharField(max_length=8, null=True)

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))

# Adds months to a given date
def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    hour = sourcedate.hour
    minute = sourcedate.minute
    second = sourcedate.second
    return datetime.datetime(year,month,day,hour,minute,second)

# Converts a timedelta into weeks with decimals
def toWeeks(delta):
    result = delta.days/7
    result += delta.seconds/7/(3600*24)
    result += delta.microseconds/7/(3600*24)/1000000
    return result

# Return the last second of the last day of the month of a given date
def monthEnd(date):
    result = datetime.datetime(date.year, date.month+1, 1,
            00,00,00,000000)
    return result - datetime.timedelta(0,1,0)
