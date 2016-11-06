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
from django.db.models import F, Q, Sum

# ****************************************************************
# ********************** GLOBAL VARIABLES ************************
# ****************************************************************

# Return the last second of the last day of the month of a given date
def month_end(date):
    result = datetime.datetime(date.year, date.month+1, 1,
            00,00,00,000000).replace(tzinfo=pytz.utc)
    return result - datetime.timedelta(0,1,0)

# Converts a timedelta into days, with decimals
def to_days(delta):
    return delta / datetime.timedelta(days=1)

# Adds months to a given date
def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.datetime(year,month,day,
            sourcedate.hour,sourcedate.minute,sourcedate.second)

today = datetime.datetime.today().replace(tzinfo=pytz.utc)
TM_end = month_end(today)
LM_end = month_end(add_months(today,-1))
TM_start = LM_end
LM_start = month_end(add_months(today,-2))
TM_days = to_days(TM_end - TM_start)
LM_days = to_days(LM_end - LM_start)

tolerance = 1

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

    # *** FILTERS ***

    # New accounts
    @cached_property
    def new_TM(self): return self.filter(reg_date__gt = TM_start)
    @cached_property
    def new_LM(self): return self.filter(
            reg_date__gt = LM_start,
            reg_date__lt = LM_end)

    # Active accounts
    @cached_property
    def active(self): return self.filter(Q(status = 'e') | Q(status = 'd'))
    @cached_property
    def active_TM(self): return self.filter(
            Q(payment__date__lt = TM_start), 
            Q(payment__paid_left__gt = 0)
            ).distinct()
    @cached_property
    def active_LM(self): return self.filter(
            Q(payment__date__lt = LM_start), 
            Q(payment__paid_left__gt = 0)
            ).distinct()

    # Accounts at risk
    def at_risk(self, days, tol):
        return self.active.last_payments.filter(
                next_disable__lt = today - datetime.timedelta(days=days + tol))

    # *** QUERYSET UNIQUE METHODS ***

    @cached_property
    def plan_tot(self):
        if not self: return 0
        return self.aggregate(Sum('plan_tot'))['plan_tot__sum']

    @cached_property
    def plan_up(self):
        if not self: return 0
        return self.aggregate(Sum('plan_up'))['plan_up__sum']

    # Returns the number of units sold
    @cached_property
    def nb_sold(self): return self.count()

    # Returns the average price
    @cached_property
    def avg_price(self): 
        if not self: return 0
        return ratio(self.plan_tot,self.nb_sold)

    # *** METHODS ***

    # Caching payments queryset
    @cached_property
    def payments(self): 
        return Payment.objects.filter(account__in = self)

    @cached_property
    def last_payments(self): 
        return self.payments.filter(is_last = True)

    # Total amount paid
    @property
    def paid(self): return self.payments.sum_amount
    @property
    def paid_EOLM(self): return self.payments.EOLM.sum_amount
    @property
    def paid_EOLLM(self): return self.payments.EOLLM.sum_amount
    @property
    def paid_TM(self): return self.payments.TM.sum_amount
    @property
    def paid_LM(self): return self.payments.LM.sum_amount

    # Outstanding balance
    @cached_property
    def outstanding(self):
        Q = self.active.last_payments
        if not Q: return 0
        return Q.aggregate(Sum('paid_left'))['paid_left__sum']

    # Expected payment according to initial plan
    def ex_plan_at(self, date):
        Q = self.filter(reg_date__lt = date)
        result = 0 
        for acc in Q:
            result += acc.ex_plan_at(date)
        return result
    @property
    def ex_plan(self): return self.ex_plan_at(today)
    @property
    def ex_plan_EOLM(self): return self.ex_plan_at(LM_END)

    # Returns the monthly expected collection for a list of accounts
    @property
    def ex_collect_TM(self):
        Q = self.active_TM
        result = 0
        for acc in Q:
            result += acc.ex_collect_TM
        return result

    @property
    def ex_collect_TM_today(self):
        Q = self.active_TM
        result = 0
        for acc in Q:
            result += acc.ex_collect_TM_today
        return result

    @property
    def ex_collect_LM(self):
        Q = self.active_LM
        result = 0
        for acc in Q:
            result += acc.ex_collect_LM
        return result

    # Repayment ratios
    @property
    def soft_repayR(self): 
        return self.paid / self.ex_plan
    @property
    def repayR(self):
        return (self.paid - self.plan_up) / (self.ex_plan - self.plan_up)
    @property
    def soft_repayR_EOLM(self): 
        return self.paid_EOLM / self.ex_plan_EOLM
    @property
    def repayR_EOLM(self):
        if self.is_new_TM: return 0
        return (self.paid_EOLM - self.plan_up) / (self.ex_plan_EOLM - self.plan_up)
    @property
    def soft_collectR_TM(self):
        return self.paid_TM / self.ex_collect_TM
    @property
    def soft_collectR_LM(self):
        return self.paid_LM / self.ex_collect_LM
    @property
    def collectR_TM(self):
        if self.is_new_TM:
            return (self.paid_TM - self.plan_up) / (self.ex_collect_TM - self.plan_up)
        else: return self.soft_collectR_TM
    @property
    def collectR_LM(self):
        if self.is_new_LM:
            return (self.paid_LM - self.plan_up) / (self.ex_collect_LM - self.plan_up)
        return self.soft_collectR_LM

    # Returns the number of accounts disabled for more than X days
    def AAR(self, days, tol):
        return self.at_risk(days,tol).count()
    @cached_property
    def AAR_7(self): return self.AAR(7, tolerance)
    @cached_property
    def AAR_14(self): return self.AAR(14, tolerance)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    def PAR(self, days, tol):
        return ratio(self.at_risk(days,tol).outstanding_balance,
                self.outstanding_balance, dec=2,pc=True,toStr=True)
    @cached_property
    def PAR_7(self): return self.PAR(7)
    @cached_property
    def PAR_14(self): return self.PAR(14)

    # Returns the number of accounts disabled for more than X days
    def ADP(self, days):
        return len([obj for obj in self.active if obj.days_disabled_tot >= days])
    @cached_property
    def ADP_14(self): return self.ADP(14)
    @cached_property
    def ADP_30(self): return self.ADP(30)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    def PDP(self, days):
        Q = [obj for obj in self.active if obj.days_disabled_tot >= days]
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

    # *** FILTERS ***

    @property
    def is_new_TM(self): return self.reg_date >= TM_start
    @property
    def is_new_LM(self): return self.reg_date >= LM_start and not self.is_new_TM

    @property
    def is_active(self): return self.last_pay.paid_left > 0
    @property
    def is_active_TM(self): 
        if self.is_new_TM: return True
        return self.last_pay_at(TM_start).paid_left > 0
    @property
    def is_active_LM(self): 
        if self.is_new_TM: return False
        if self.is_new_LM: return True
        return self.last_pay_at(LM_start).paid_left > 0

    # *** METHODS ***

    # Payments
    @cached_property
    def payments(self):
        return Payment.objects.filter(account = self).order_by('date').reverse()

    def last_pay_at(self, date):
        try: return self.payments.filter(date__lt = date)[0]
        except: return None

    @cached_property
    def last_pay(self): return self.last_pay_at(today)

    # Credit
    def credit_at(self,date):
        try: return max(0,to_days(self.last_pay_at(date).next_disable - date))
        except: return 0

    @cached_property
    def credit(self): return credit(self,today)

    # Total days disabled
    @cached_property
    def days_disabled_tot(self):
        result = min(0,to_days(self.last_pay_at(date).next_disable - today))
        for pay in self.payments: result += min(0, pay.days_left_before)
        return result

    # Total amount paid
    def paid_at(self, date):
        try: return self.last_pay.at(date).paid_after
        except: return 0
    @cached_property
    def paid(self): return self.last_payment.paid_after
    @property
    def paid_EOLM(self): 
        return self.payments.EOLM.sum_amount
    @property
    def paid_EOLLM(self): 
        return self.payments.EOLLM.sum_amount
    @property
    def paid_TM(self): return self.payments.TM.sum_amount
    @property
    def paid_LM(self): return self.payments.LM.sum_amount

    # Outstanding balance
    @property
    def outstanding(self): return self.plan_tot - self.paid

    # Expected payment according to initial plan
    def ex_plan_at(self, date):
        if date < self.reg_date: return 0
        full_weeks = int(to_weeks(date - self.reg_date))
        return min(self.plan_up + self.plan_week*full_weeks, self.plan_tot)
    @property
    def ex_plan(self): return self.ex_plan_at(today)
    @property
    def ex_plan_EOLM(self): return self.ex_plan_at(LM_end)

    # Expected payment according to initial plan or best
    @property
    def ex_plan_or(self): return max(self.ex_plan_at(today), self.paid)
    @property
    def ex_plan_EOLM_or(self): return max(self.ex_plan_at(LM_end),
            self.paid_at(LM_end))

    # Expected collection
    @property
    def ex_collect_TM(self):
        if not self.is_active_TM: return 0
        if self.is_new_TM: return self.ex_plan_at(TM_end)
        return max(int((TM_days - self.credit_at(TM_start))/7 + 1)*
                self.plan_week, self.paid_TM)

    @property
    def ex_collect_TM_today(self):
        if not self.is_active_TM: return 0
        if self.is_new_TM: return self.ex_plan_at(today)
        days = to_days(today - TM_start)
        return max(int((days - self.credit_at(TM_start))/7 + 1)*
                self.plan_week, self.paid_TM)

    @property
    def ex_collect_LM(self):
        if not self.is_active_LM: return 0
        if self.is_new_TM: return 0
        if self.is_new_LM: return self.ex_plan_at(LM_end)
        return max(int((LM_days - self.credit_at(LM_start))/7 + 1)*
                self.plan_week, self.paid_LM)

    # Repayment ratios
    @property
    def soft_repayR(self): 
        return self.paid / self.ex_plan
    @property
    def repayR(self):
        return (self.paid - self.plan_up) / (self.ex_plan - self.plan_up)
    @property
    def soft_repayR_EOLM(self): 
        return self.paid_EOLM / self.ex_plan_EOLM
    @property
    def repayR_EOLM(self):
        if self.is_new_TM: return 0
        return (self.paid_EOLM - self.plan_up) / (self.ex_plan_EOLM - self.plan_up)
    @property
    def soft_collectR_TM(self):
        return self.paid_TM / self.ex_collect_TM
    @property
    def soft_collectR_LM(self):
        return self.paid_LM / self.ex_collect_LM
    @property
    def collectR_TM(self):
        if self.is_new_TM:
            return (self.paid_TM - self.plan_up) / (self.ex_collect_TM - self.plan_up)
        else: return self.soft_collectR_TM
    @property
    def collectR_LM(self):
        if self.is_new_LM:
            return (self.paid_LM - self.plan_up) / (self.ex_collect_LM - self.plan_up)
        return self.soft_collectR_LM

# CREDIT SCORING

    # Socio economic score
    @property
    def score_social(self):
        if self.client.gender == 'M': return 0.43
        elif self.client.gender == 'F': return 0.62
        else: return 0.5

    # Total disablement score
    @property
    def score_disable(self):
        return (42-min(self.days_disabled_tot,42))/42

    # Max payment score
    @property
    def score_bullet(self):
        max_pay = list(self.payments.order_by('amount')[:1])[0].amount
        return min(max_pay,100000)/100000

    # Combined score
    @property
    def score(self):
        weight_social = 0.2
        weight_disable = 0.8
        weight_bullet = 0.3
        return ((self.score_social * weight_social 
                + self.score_disable * weight_disable
                + self.score_bullet * weight_bullet)
                / (weight_social + weight_disable + weight_bullet))

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

    # Filtering payments by date
    @property
    def TM(self): return self.filter(date__gt = TM_start)
    @property
    def EOLM(self): return self.filter(date__lt = LM_end)
    @property
    def LM(self): return self.filter(date__gt = LM_start, date__lt = LM_end)
    @property
    def EOLLM(self): return self.filter(date__lt = LM_start)

    # Returns the number of payments, this month and last month
    @cached_property
    def nb(self): return self.count()

    # Returns the total payment amount
    @cached_property
    def sum_amount(self):
        if not self: return 0
        return self.aggregate(Sum('amount'))['amount__sum']

    # Returns the average payment amount
    @cached_property
    def average_payment(self):
        if not self: return 0
        return ratio(self.sum_amount,self.nb,toStr=True)

# SIMPLE PAYMENT CLASS, INCLUDES ANGAZA ID TO USE AS PRIMARY KEY WHEN UPDATING
class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    id_Angaza = models.CharField(max_length=8, null=True)
    agent = models.ForeignKey(Agent)
    # convenience fields to avoid querying all the payments each time
    days_left_before = models.FloatField(default=0, null=True)
    next_disable = models.DateTimeField('next disable date', null=True)
    paid_after = models.PositiveIntegerField(default=0, null=True)
    paid_left = models.PositiveIntegerField(default=0, null=True)
    is_last = models.NullBooleanField()
    # manager
    objects = PaymentQuerySet.as_manager()

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))

    # Returns True if the payment was collected this month
    @property
    def is_TM(self): return is_this_month(self.date,0)
    @property
    def is_LM(self): return is_this_month(self.date,-1)

    # Returns True is the payment is an upfront payment
    @property
    def is_upfront(self):
        return self.account.payments.filter(date__lt = self.date).count() == 0

    # Returns the value in days of credit for a "normal" payment
    @property
    def days_value(self): return (self.amount/self.account.plan_week) * 7
    # Returns the value in days of credit of a payment for a deposit
    @property
    def days_value_up(self): 
        return ((self.amount - self.account.plan_up)
                / self.account.plan_week + 1) * 7

# UPDATES THE CREDIT_AFTER FIELD WHEN A PAYMENT IS CREATED
@receiver(post_save, sender=Payment,
        dispatch_uid='Payment_save_signal')
def record_payment(sender, instance, created, *args, **kwargs):
    if created:
        payments = (instance.account.payments.filter(date__lt = instance.date)
                .order_by('date'))

        if not payments:
            instance.credit_before = 0
            instance.paid_after = instance.amount
            instance.next_disable = instance.date + datetime.timedelta(
                    days=instance.days_value_up)

        else:
            last_pay = payments[0]
            instance.credit_before = to_days(
                    last_pay.next_disable - instance.date)
            instance.paid_after = last_pay.paid_after + instance.amount
            instance.next_disable = (max(instance.date, last_pay.next_disable) 
                    + datetime.timedelta(days=instance.days_value))
            last_pay.is_last = False
            last_pay.save()

        instance.paid_left = instance.account.plan_tot - instance.paid_after
        instance.is_last = True
        instance.save()

# ****************************************************************
# ********************** CUSTOM METHODS **************************
# ****************************************************************

# Converts a timedelta into weeks, with decimals
def to_weeks(delta):
    result = delta.days/7
    result += delta.seconds/7/(3600*24)
    result += delta.microseconds/7/(3600*24)/1000000
    return result

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
