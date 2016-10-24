from django.db import models
import math
# Imports to handle dates and timezones
import datetime, calendar, pytz
# Some models from the sales app are imported in inventory.models which can
# create a circular import error
from inventory.models import (Product, Warehouse, Transaction, 
        TransactionItem, InventoryItem)
# Imports to receive the post_save signal and create transactions on sale
from django.db.models.signals import post_save
from django.dispatch import receiver
# Used to cache properties and improve performance
from django.utils.functional import cached_property
# Complex queries and filters
from django.db.models import Q, Sum

# ****************************************************************
# ************************** CLIENT ******************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE ACCOUNT CLASS TO DEFINE TABLE LEVEL METHODS
class ClientQuerySet(models.QuerySet):

    @cached_property
    def nb(self): return self.count()
    @cached_property
    def nb_new_TM(self): return len([obj for obj in self if obj.is_new_TM])
    @cached_property
    def nb_new_LM(self): return len([obj for obj in self if obj.is_new_LM])

    @cached_property
    def account_per_client(self):
        nb_accounts = Account.objects.filter(client__in = self).count()
        nb_clients = self.nb
        return ratio(nb_accounts,nb_clients,dec=2,toStr=True)

# SIMPLE CLIENT CLASS
# At the moment only handles 1 phone number per client and uses it as the main
# key (used to identify duplicates, never updated)
# Would probably need to implement a double search on update to manage that
# properly (update phone if other fields are similar)
# Also have to look into addons to identify and merge duplicates
class Client(models.Model):
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    phone = models.CharField(max_length=16, null=True)
    location = models.CharField(max_length=30, null=True)
    objects = ClientQuerySet.as_manager()

    def __str__(self):
        return ('%s (%s)' % (self.name, self.location))

    # Returns the earliest registration date
    @property
    def first_registration(self):
        result = datetime.datetime.today().replace(tzinfo=pytz.utc)
        for acc in Account.objects.filter(client=self):
            result = min(acc.reg_date,result)
        return result

    # Returns True if the client was created a given month offset from today
    def is_new_by_month(self,offset): 
        return is_this_month(self.first_registration,offset)
    @property
    def is_new_TM(self): return self.is_new_by_month(0)
    @property
    def is_new_LM(self): return self.is_new_by_month(-1)

# ****************************************************************
# ************************* MANAGER ******************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE MANAGER CLASS TO DEFINE TABLE LEVEL METHODS
class ManagerQuerySet(models.QuerySet):
    
    def top_seller_list(self):
        managers = Manager.objects.all()
        accounts = Account.objects.all()
        for man in managers:
            rev = (accounts.filter(agent__manager = man)).revenue

# MANAGER CLASS, RESPONSIBLE FOR SEVERAL AGENTS
class Manager(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    start_date = models.DateTimeField('date hired')
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')))
    district = models.CharField(max_length=30)
    phone = models.CharField(max_length=16)
    objects = ManagerQuerySet.as_manager()

    def __str__(self):
        return ('%s %s (%s)' % (self.firstname, self.lastname, self.district))

# ****************************************************************
# ************************** AGENT *******************************
# ****************************************************************

# AGENT CLASS, SELLS PRODUCTS FROM A UNIQUE WAREHOUSE
# Could look into geolocalization...
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

# ****************************************************************
# ************************* ACCOUNT ******************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE ACCOUNT CLASS TO DEFINE TABLE LEVEL METHODS
class AccountQuerySet(models.QuerySet):

    # Filtering new accounts
    def new(self,start,end):
        return self.filter(reg_date__lt = end, reg_date__gt = start)
    @cached_property
    def new_TM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        month_start = month_end(add_months(today,-1))
        return self.filter(reg_date__gt = month_start)
    @cached_property
    def new_LM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eolm = month_end(add_months(today,-1))
        bolm = datetime.datetime(eolm.year,eolm.month,1,0,0,0)
        return self.filter(reg_date__gt = bolm, reg_date__lt = eolm)

    # Filtering active accounts
    @cached_property
    def active(self):
        return self.filter(Q(status = 'e') | Q(status = 'd'))
    @cached_property
    def active_TM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        month_start = month_end(add_months(today,-1))
        return self.filter(Q(status = 'e') 
                | Q(status = 'd')
                | Q(payment__date__gt = month_start)).distinct()

    # Returns the number of units sold, this month and last month
    @cached_property
    def nb_sold(self): return self.count()

    # Returns the total "revenue" (total sold)
    @cached_property
    def revenue(self): 
        if not self: return 0
        return self.aggregate(Sum('plan_tot'))['plan_tot__sum']

    # Returns the monthly expected collection for a list of accounts
    @cached_property
    def expct_collection_TM(self):
        result = 0
        for account in self.active_TM:
            result+= (account.expct_paid_TM - min(0,account.payment_deficit))
        return result

    # Returns the amount collected this month in upfront payments
    @cached_property
    def collected_upfront(self):
        Q = self.new_TM
        if not Q: return 0
        return Q.aggregate(Sum('plan_up'))['plan_up__sum']

    # Returns this month's upfront payments as a % of expected collection
    @property
    def collected_upfront_PCT(self):
        return ratio(self.collected_upfront, self.expct_collection_TM,
                pc=True)

    # Returns the amount collected this month in instalments
    @cached_property
    def collected_instalments(self):
        Q = Payment.objects.filter(account__in = self.active_TM).TM
        if not Q: return 0
        result = Q.aggregate(Sum('amount'))['amount__sum']
        return result - self.collected_upfront

    # Returns this month's instalments as a % of expected collection
    @property
    def collected_instalments_PCT(self):
        return ratio(self.collected_instalments, self.expct_collection_TM,
                pc=True)

    # Returns the amount of late payments for this month
    @cached_property
    def collected_late(self):
        result = 0
        for account in self.active_TM:
            result += max(0,account.payment_deficit)
        return result

    # Returns this month's instalments as a % of expected collection
    @property
    def collected_late_PCT(self):
        return ratio(self.collected_late, self.expct_collection_TM,
                pc=True)

    # Returns the amount of repayments outstanding
    @cached_property
    def outstanding_balance(self):
        if not self: return 0
        paid = (Payment.objects.filter(account__in = self)
                .aggregate(Sum('amount'))['amount__sum'])
        return self.revenue - paid

    # Returns the number of accounts disabled for more than X days
    # Accounts At Risk
    def AAR(self, days):
        return len([obj for obj in self.active 
            if obj.days_disabled_current >= days])

    @cached_property
    def AAR_7(self): return self.AAR(7)

    @cached_property
    def AAR_14(self): return self.AAR(14)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    # Portfolio At Risk
    def PAR(self, days):
        Q = [obj for obj in self if obj.days_disabled_current >= days]
        par = 0
        for account in Q:
            par += account.plan_tot - account.paid
        return ratio(par,self.outstanding_balance,
                dec=2,pc=True,toStr=True)

    @cached_property
    def PAR_7(self): return self.PAR(7)

    @cached_property
    def PAR_14(self): 
        return self.PAR(14)

    # Returns the number of accounts disabled for more than X days
    # Accounts At Risk
    def ADP(self, days):
        return len([obj for obj in self.active if obj.days_disabled >= days])

    @cached_property
    def ADP_14(self): return self.ADP(14)

    @cached_property
    def ADP_30(self): return self.ADP(30)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    # Portfolio At Risk
    def PDP(self, days):
        Q = [obj for obj in self.active if obj.days_disabled >= days]
        pdp = 0
        for account in Q:
            pdp += account.plan_tot - account.paid
        return ratio(pdp,self.outstanding_balance,
                dec=2,pc=True,toStr=True)

    @cached_property
    def PDP_14(self): return self.PDP(14)

    @cached_property
    def PDP_30(self): return self.PDP(30)

# SIMPLE ACCOUNT CLASS WITH PLENTY OF FUNCTIONS FOR ANALYTICS
# By convention, all @property methods are named get_ to not be confused with
# class attributes
# AccountQuerySet is a custom query set created to add table level methods
# Model doesn't work yet with replaced lamps
# Also, test accounts are not taken into account at this stage
# PLAN is not a separate class because of how plans can change over time and
# it would be a nightmare to track (they keep the same name on the hub)
class Account(models.Model):
    STATUS = (('e', 'Enabled'), ('d', 'Deactivated'), 
            ('u', 'Unlocked'), ('w', 'Written Off'),
            ('r', 'Reposessed'))

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
    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return '%s - %s' % (self.account_GLP, self.plan_name)

    # Caching payments queryset
    @cached_property
    def payments(self):
        return Payment.objects.filter(account = self)

    # Total amount paid
    @cached_property
    def paid(self):
        Q = self.payments
        if not Q: return 0
        return (Q.aggregate(Sum('amount'))['amount__sum'])
    @cached_property
    def paid_TM(self): 
        Q = self.payments.TM
        if not Q: return 0
        return (Q.aggregate(Sum('amount'))['amount__sum'])
    @cached_property
    def paid_LM(self): 
        Q = self.payments.LM
        if not Q: return 0
        return (Q.aggregate(Sum('amount'))['amount__sum'])

    # Total number of payments
    @cached_property
    def payment_nb(self):
        return Payment.objects.filter(account = self).count()
    def payment_nb_TM(self):
        return Payment.objects.filter(account = self).TM.count()
    def payment_nb_LM(self):
        return Payment.objects.filter(account = self).LM.count()

    # Outstanding balance
    @cached_property
    def left_to_pay(self):
        return self.plan_tot - self.paid

    # Expected payment as of 'date'
    def expct_paid_at_date(self, date):
        if date < self.reg_date:
            return 0
        delta = date - self.reg_date
        full_weeks = int(to_weeks(delta))
        return min(self.plan_up + self.plan_week*full_weeks, self.plan_tot)

    # Expected payment as of today
    @property
    def expct_paid(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        return self.expct_paid_at_date(today)

    # Expected payment as of end of month
    @property
    def expct_paid_TM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eom = month_end(today)
        return (self.expct_paid_at_date(eom) 
                - self.paid 
                + self.paid_TM)

    # Expected payment as of end of last month
    @property
    def expct_paid_LM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eolm = month_end(add_months(today,-1))
        return (self.expct_paid_at_date(eolm) 
                - self.paid 
                + self.paid_TM + self.paid_LM)

    # Returns True if the account was created a given month offset from today
    def is_new_by_month(self,offset): return is_this_month(self.reg_date,offset)
    @property
    def is_new_TM(self): return self.is_new_by_month(0)
    @property
    def is_new_LM(self): return self.is_new_by_month(-1)

    # Payment deficit, can be negative if in advance
    @property
    def payment_deficit(self): return self.expct_paid - self.paid
    @property
    def payment_deficit_TM(self): return self.expct_paid_TM - self.paid_TM
    @property
    def payment_deficit_LM(self): return self.expct_paid_LM - self.paid_LM

    # Returns a Payment object with the last payment
    @cached_property
    def last_payment(self):
        r = list(Payment.objects.filter(account = self).order_by('date')[:1])
        if r:
            return r[0]
        return None

    @cached_property
    def days_credit(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        for idx, payment in enumerate(
                Payment.objects.filter(account = self).order_by('date')):
            if idx == 0:
                weeks_credit = ((payment.amount - self.plan_up)/self.plan_week 
                        + 1)
                disable_date = (payment.date 
                        + datetime.timedelta(weeks_credit*7,0,0))
            else:
                weeks_credit = payment.amount / self.plan_week
                disable_date = (max(disable_date, payment.date) 
                        + datetime.timedelta(weeks_credit*7,0,0))
            prev_pay = payment
        result = 0
        if self.status != 'u':
            result += to_weeks(today - disable_date)*7
        return result

    # Total numbers of days disabled. Returns the current disabled if now = True
    # tolerance is the number of days of disablement before it starts counting
    def days_disabled_main(self, tolerance = 0, now = False):
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
                result += max(
                        to_weeks(payment.date - disable_date)*7 - tolerance,0)
                weeks_credit = payment.amount / self.plan_week
                disable_date = (max(disable_date, payment.date) 
                        + datetime.timedelta(weeks_credit*7,0,0))
            prev_pay = payment
        if now:
            result = 0
        if self.status != 'u':
            result += max(0,to_weeks(today - disable_date)*7 - tolerance)
        return result

    @cached_property
    def days_disabled(self):
        return self.days_disabled_main(tolerance=1)

    # Current disabled, made into a property for use in templates
    @cached_property
    def days_disabled_current(self): return self.days_disabled_main(
            tolerance=1, now=True)

    # False if account is not active this month
    @property
    def is_active(self):
        return (
                (self.status == 'e') 
                or (self.status == 'd')
                )

    # False if account is not active this month
    @property
    def is_active_TM(self):
        return (
                (self.status == 'e') 
                or (self.status == 'd')
                or (self.status == 'u' 
                    and is_this_month(self.last_payment.date,0)) 
                )

# CREATES A TRANSACTION AND TRANSACTION ITEM WHEN AN ACCOUNT IS CREATED
@receiver(post_save, sender=Account,
        dispatch_uid='Account_save_signal')
def log_transactions(sender, instance, created, *args, **kwargs):
    if created:
        transaction = Transaction.objects.create(
                transaction_type = 2,
                date = instance.reg_date,
                origin = instance.agent.warehouse,
                destination = Warehouse.objects.get(name="_Client"),
                account = instance,
                comment = "sale"
                )
        transItem = TransactionItem.objects.create(
                transaction = transaction,
                item = InventoryItem.objects.get(
                    product = instance.plan_product,
                    warehouse = instance.agent.warehouse),
                qty = 1
                )

# ****************************************************************
# ************************* PAYMENTS *****************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE ACCOUNT CLASS TO DEFINE TABLE LEVEL METHODS
class PaymentQuerySet(models.QuerySet):

    # Filtering payments LM and TM
    @property
    def TM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        month_start = month_end(add_months(today,-1))
        return self.filter(date__gt = month_start)
    @property
    def LM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eolm = month_end(add_months(today,-1))
        bolm = datetime.datetime(eolm.year,eolm.month,1,0,0,0)
        return self.filter(date__gt = bolm, date__lt = eolm)

    # Returns the number of payments, this month and last month
    @cached_property
    def nb(self): return self.count()

    # Returns the average payment amount
    @cached_property
    def average_payment(self):
        if not self: return 0
        total_amount = self.aggregate(Sum('amount'))['amount__sum']
        return ratio(total_amount,self.nb,toStr=True)

# SIMPLE PAYMENT CLASS, INCLUDES ANGAZA ID TO USE AS PRIMARY KEY WHEN UPDATING
class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    agent = models.ForeignKey(Agent)
    id_Angaza = models.CharField(max_length=8, null=True)
    objects = PaymentQuerySet.as_manager()

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))

    # Returns True if the account was collected this month
    @property
    def is_TM(self):
        return is_this_month(self.date,0)

    # Returns True if the account was collected last month
    @property
    def is_LM(self):
        return is_this_month(self.date,-1)

# ****************************************************************
# ********************** CUSTOM METHODS **************************
# ****************************************************************

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

# Converts a timedelta into weeks, with decimals
def to_weeks(delta):
    result = delta.days/7
    result += delta.seconds/7/(3600*24)
    result += delta.microseconds/7/(3600*24)/1000000
    return result

# Return the last second of the last day of the month of a given date
def month_end(date):
    result = datetime.datetime(date.year, date.month+1, 1,
            00,00,00,000000).replace(tzinfo=pytz.utc)
    return result - datetime.timedelta(0,1,0)

# Returns Yes if date is of today's month with offset
def is_this_month(date,offset):
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    return (date > month_end(add_months(today,-1+offset)) and
        date <= month_end(add_months(today,offset)))

# Returns the ratio of two numbers, handling div by 0 and with options on the
# number of decimals, display as pc and str output
def ratio(top, bottom, dec=0, pc=False, toStr=False):
    if not toStr:
        if bottom == 0:
            return 0
        elif pc:
            return (int(round(top/bottom,2+dec)*math.pow(10,dec+2))
                    /math.pow(10,dec))
        else:
            return (int(round(top/bottom,dec)*math.pow(10,dec))
                    /math.pow(10,dec))
    else:
        if bottom == 0:
            return "n.a."
        elif pc:
            return str((int(round(top/bottom,2+dec)*math.pow(10,dec+2))
                    /math.pow(10,dec))) + " %"
        else:
            if dec != 0:
                return str("{:,}".format(int(round(top/bottom,dec)
                    *math.pow(10,dec))/math.pow(10,dec)))
            return str("{:,}".format(int(round(top/bottom,dec))))
