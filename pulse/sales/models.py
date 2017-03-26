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
from django.db.models import F, Q, Sum, FloatField

# ****************************************************************
# ********************** GLOBAL VARIABLES ************************
# ****************************************************************

# Return the last second of the last day of the month of a given date
def month_end(date):
    result = datetime.datetime(
            date.year + int(date.month/12),
            date.month % 12 + 1,
            1,00,00,00,000000).replace(tzinfo=pytz.utc)
    return result - datetime.timedelta(0,1,0)

# Converts a timedelta into days, with decimals
def to_days(delta): return delta / datetime.timedelta(days=1)

# Adds months to a given date
def add_months(date,months):
    month = date.month - 1 + months
    year = int(date.year + month / 12 )
    month = month % 12 + 1
    day = min(date.day,calendar.monthrange(year,month)[1])
    return datetime.datetime(year,month,day,
            date.hour,date.minute,date.second)

# Global time variables
today = datetime.datetime.today().replace(tzinfo=pytz.utc)
TM_end = month_end(today)
LM_end = month_end(add_months(today,-1))
TM_start = LM_end
LM_start = month_end(add_months(today,-2))
TM_days = to_days(TM_end - TM_start)
LM_days = to_days(LM_end - LM_start)

last_friday = today - datetime.timedelta(0
        ,today.hour*60*60+today.minute*60+today.second,0)
while last_friday.weekday() != 4:
    last_friday -= datetime.timedelta(1,0,0)

# Threshold in days after ways the number of disabled days starts increasing
tolerance = 0

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
# ************************ AGENT COM *****************************
# ****************************************************************

# CLASS TO MANAGE AGENT COMMISSION
class ComPlan(models.Model):
    name = models.CharField(max_length=30)
    stipend = models.PositiveIntegerField(default=0)
    top_up = models.PositiveIntegerField(default=0)
    transport = models.PositiveIntegerField(default=0)
    trigger1 = models.PositiveIntegerField(default=0)
    bonus1 = models.PositiveIntegerField(default=0)
    trigger2 = models.PositiveIntegerField(default=0)
    bonus2 = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

# ****************************************************************
# ************************** AGENT *******************************
# ****************************************************************

# AGENT CLASS, SELLS PRODUCTS FROM A UNIQUE WAREHOUSE
class Agent(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    start_date = models.DateTimeField('date hired')
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    category = models.CharField(max_length=1,
            choices=(('R', 'Rural'), ('F', 'Freetown'), ('H', 'HQ'), 
                ('O', 'Other')), null=True)
    location = models.CharField(max_length=30)
    warehouse = models.ForeignKey(Warehouse)
    phone = models.CharField(max_length=16)
    manager = models.ForeignKey(Manager)
    login = models.CharField(max_length=30, null=True)
    label = models.CharField(max_length=50, null=True)
    com = models.ForeignKey(ComPlan, null=True)

    def __str__(self):
        return ('%s (%s %s)' % (self.location, self.firstname, self.lastname))

    # Returns the queryset of accounts managed by a given agent
    @cached_property
    def accounts(self):
        return Account.objects.filter(agent=self)

    # Returns the number of sales made 'delta' weeks before the current one
    def sales_week(self, delta):
        if delta == 0:
            return (self.accounts.new(last_friday,today).
                    exclude(status = 'r').exclude(status = 'w').nb)
        else:
            return (self.accounts.new(
                last_friday - datetime.timedelta((delta)*7,0,0),
                last_friday - datetime.timedelta((delta-1)*7,0,0)).
                exclude(status = 'r').exclude(status = 'w').nb)

    def com_week(self, delta):
        value = self.com.stipend + self.com.top_up + self.com.transport
        if self.sales_week(delta) >= self.com.trigger1:
            value += self.com.bonus1
        if self.sales_week(delta) >= self.com.trigger2:
            value += self.com.bonus2
        return value

# ****************************************************************
# ************************** CLIENT ******************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE CLIENT CLASS TO DEFINE TABLE LEVEL METHODS
class ClientQuerySet(models.QuerySet):

    @cached_property
    def nb(self): return self.count()
    @cached_property
    def nb_new_TM(self): return len([obj for obj in self if obj.is_new_TM])
    @cached_property
    def nb_new_LM(self): return len([obj for obj in self if obj.is_new_LM])

    @cached_property
    def account_per_client(self):
        Q = self.exclude(account__agent__login__in = 
                ['hq.freetown', 'hq.demo', 'hq.marketing'])
        nb_accounts = Account.objects.filter(client__in = Q).count()
        nb_clients = Q.nb
        return ratio(nb_accounts,nb_clients,dec=2,toStr=True)

# SIMPLE CLIENT CLASS
# At the moment only handles 1 phone number per client and uses it as the main
# key (used to identify duplicates, never updated)
# Would probably need to implement a double search on update to manage that
# properly (update phone if other fields are similar?)
# Also have to look into addons to identify and merge duplicates
class Client(models.Model):
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    phone = models.CharField(max_length=16, null=True)
    location = models.CharField(max_length=50, null=True)
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

    @property
    def nb_accounts(self):
        return Account.objects.filter(client=self).count()

    # Returns True if the client was created a given month offset from today
    def is_new_by_month(self,offset): 
        return is_this_month(self.first_registration,offset)
    @property
    def is_new_TM(self): return self.is_new_by_month(0)
    @property
    def is_new_LM(self): return self.is_new_by_month(-1)

# ****************************************************************
# ************************* ACCOUNT ******************************
# ****************************************************************

# CUSTOM QUERYSET CLASS FOR THE ACCOUNT CLASS TO DEFINE TABLE LEVEL METHODS
class AccountQuerySet(models.QuerySet):

    # *** FILTERS ***

    # New accounts
    def new(self,start,end): return self.filter(
            reg_date__gt = start,
            reg_date__lt = end)
    @cached_property
    def new_TM(self): return self.filter(reg_date__gt = TM_start)
    @cached_property
    def not_new_TM(self): return self.filter(reg_date__lt = TM_start)
    @cached_property
    def new_LM(self): return self.new(LM_start,LM_end)
    @cached_property
    def not_new_LM(self): return self.exclude(
            reg_date__gt = LM_start,
            reg_date__lt = LM_end)

    # Credit and cash accounts
    @property
    def cash(self): return self.filter(plan_iscash = True)
    @property
    def credit(self): return self.exclude(plan_iscash = True)

    # Unlocked accounts
    def unlocked_between(self, start, end):
        return self.filter(unlock_date__gt = start, unlock_date__lt = end)
    @property
    def unlocked_TM(self):
        return self.unlocked_between(TM_start,today)
    @property
    def unlocked_LM(self):
        return self.unlocked_between(LM_start, LM_end)

    # Active accounts
    @cached_property
    def active(self): return self.filter(Q(status = 'e') | Q(status = 'd'))
    @cached_property
    def active_TM(self): 
        pays = self.payments.filter(date__lt = TM_start, paid_left = 0)
        return self.exclude(payment__in = pays)
    @cached_property
    def active_LM(self):
        pays = self.payments.filter(date__lt = LM_start, paid_left = 0)
        return self.not_new_TM.exclude(payment__in = pays)

    # Accounts at risk
    def at_risk(self, days, tol):
        return self.filter(payment__in = 
                self.active.last_payments.filter(next_disable__lt = 
                    today - datetime.timedelta(days = days + tol)))

    # Accounts with delayed payments
    def delayed_payment(self, days, tol):
        return self.filter(payment__in = 
                self.active.last_payments.filter(
                    Q(perfect_date__lt = F('next_disable') -
                        datetime.timedelta(days = days + tol)) |
                    Q(perfect_date__lt = today -
                        datetime.timedelta(days = days + tol))))

    # *** QUERYSET UNIQUE METHODS ***

    @cached_property
    def plan_tot(self):
        if not self.exists(): return 0
        return self.aggregate(Sum('plan_tot'))['plan_tot__sum']

    @cached_property
    def plan_up(self):
        if not self.exists(): return 0
        return self.aggregate(Sum('plan_up'))['plan_up__sum']

    # Returns the number of units sold
    @cached_property
    def nb(self): return self.count()

    # Returns the average price
    @cached_property
    def avg_price(self): 
        if not self.exists(): return 0
        return int(ratio(self.plan_tot,self.nb))

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
        if not Q.exists(): return 0
        return Q.aggregate(Sum('paid_left'))['paid_left__sum']
    @property
    def outstanding_at_EOLM(self):
        result = 0
        for acc in self.active_LM:
            result += acc.outstanding_at(LM_end)
        return result
    @property
    def outstanding_at_EOLLM(self):
        result = 0
        for acc in self.active_LM:
            result += acc.outstanding_at(LM_start)
        return result

    @property
    def nb_active_at_EOLM(self):
        result = 0
        return len([acc for 
            acc in self.active_LM if acc.is_active_at(LM_end)])
    @property
    def nb_active_at_EOLLM(self):
        result = 0
        return len([acc for 
            acc in self.active_LM if acc.is_active_at(LM_start)])

    # Expected payment according to initial plan
    def ex_plan_at2(self, date):
        Q = self.filter(reg_date__lt = date)
        return Q.aggregate(ex_plan = Sum(F('plan_up') +
            F('plan_week')*int(to_weeks(date - F('reg_date')))),
            output_field=FloatField())
    @property
    def ex_plan2(self): return self.ex_plan_at2(today)

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
    def ex_plan_EOLM(self): return self.ex_plan_at(LM_end)

    # Returns the monthly expected collection for a list of accounts

    @cached_property
    def ex_paid_TM(self):
        Q = self.active_TM
        result = 0
        for acc in Q:
            result += acc.ex_paid_TM
        return result
    @cached_property
    def ex_paid_TM_today(self):
        Q = self.active_TM
        result = 0
        for acc in Q:
            result += acc.ex_paid_TM_today
        return result
    @property
    def ex_paid_LM(self):
        Q = self.active_LM
        result = 0
        for acc in Q:
            result += acc.ex_paid_LM
        return result

    @cached_property
    def ex_collect(self):
        result = 0
        for acc in self.active:
            result += acc.ex_collect
        return result
    @cached_property
    def ex_collect_TM(self):
        result = 0
        for acc in self.active_TM:
            result += acc.ex_collect_TM
        return result
    @cached_property
    def ex_collect_TM_today(self):
        result = 0
        for acc in self.active_TM:
            result += acc.ex_collect_TM_today
        return result
    @property
    def ex_collect_LM(self):
        result = 0
        for acc in self.active_LM:
            result += acc.ex_collect_LM
        return result

    # Repayment ratios
    @property
    def repayR(self):
        Q = self.active
        return ratio(Q.paid - Q.plan_up, Q.ex_plan - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def repayR_TM(self):
        Q = self.new_TM
        return ratio(self.paid_TM - Q.plan_up, self.ex_paid_TM - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def repayR_TM_today(self):
        Q = self.new_TM
        return ratio(self.paid_TM - Q.plan_up, self.ex_paid_TM_today - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def repayR_LM(self):
        Q = self.new_LM
        return ratio(self.paid_LM - Q.plan_up, self.ex_paid_LM - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def collectR(self):
        Q = self.active
        return ratio(Q.paid - Q.plan_up, Q.ex_collect - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def collectR_TM(self):
        Q = self.new_TM
        return ratio(self.paid_TM - Q.plan_up, self.ex_collect_TM - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def collectR_TM_today(self):
        Q = self.new_TM
        return ratio(self.paid_TM - Q.plan_up, self.ex_collect_TM_today - Q.plan_up,
                dec=0, pc=True, toStr=True)
    @property
    def collectR_LM(self):
        Q = self.new_LM
        return ratio(self.paid_LM - Q.plan_up, self.ex_collect_LM - Q.plan_up,
                dec=0, pc=True, toStr=True)

    # Variables for progress bars
    @cached_property
    def graph_collectR_TM(self):
        Q = self.new_TM
        return ratio(self.paid_TM - Q.plan_up,
                self.ex_collect_TM - Q.plan_up,
                dec=0, pc=True)

    @cached_property
    def graph_collect_TM(self):
        Q = self.new_TM
        return self.paid_TM - Q.plan_up

    @property
    def graph_lateR_TM(self):
        Q = self.new_TM
        return ratio(self.ex_collect_TM_today - self.paid_TM,
                self.ex_collect_TM - Q.plan_up,
                dec=0, pc=True)

    @property
    def graph_late_TM(self):
        return self.ex_collect_TM_today - self.paid_TM

    # Returns the number of accounts disabled for more than X days
    def AAR(self, days, tol):
        return self.at_risk(days,tol).count()
    @cached_property
    def AAR_0(self): return self.AAR(0, tolerance)
    @cached_property
    def AAR_7(self): return self.AAR(7, tolerance)
    @cached_property
    def AAR_14(self): return self.AAR(14, tolerance)
    @cached_property
    def AAR_31(self): return self.AAR(31, tolerance)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    def PAR(self, days, tol):
        return ratio(self.at_risk(days,tol).outstanding,
                self.outstanding, dec=1,pc=True,toStr=True)
    @cached_property
    def PAR_0(self): return self.PAR(0, tolerance)
    @cached_property
    def PAR_7(self): return self.PAR(7, tolerance)
    @cached_property
    def PAR_14(self): return self.PAR(14, tolerance)
    @cached_property
    def PAR_31(self): return self.PAR(31, tolerance)

    # Returns the number of accounts disabled for more than X days
    def ADP(self, days, tol):
        return self.delayed_payment(days,tol).count()
    @cached_property
    def ADP_30(self): return self.ADP(30, tolerance)

    # Returns the PCT of outstanding balance for accounts disabled for more
    # than X days
    def PDP(self, days, tol):
        return ratio(self.delayed_payment(days,tol).outstanding,
                self.outstanding, dec=2,pc=True,toStr=True)
    @cached_property
    def PDP_30(self): return self.PDP(30, tolerance)

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
    plan_iscash = models.NullBooleanField()
    reg_date = models.DateTimeField('registration date')
    unlock_date = models.DateTimeField('unlock date', null=True)
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
    def is_active_at(self,date): 
        if self.reg_date < date:
            return self.last_pay_at(date).paid_left > 0
        return False
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
    def credit(self): return self.credit_at(today)

    @cached_property
    def credit_relative(self): return to_days(self.last_pay.next_disable -today)

    @cached_property
    def days_disabled_now(self): 
        if self.is_active: return -to_days(self.last_pay.next_disable -today)
        return 0

    # Total days disabled
    @cached_property
    def days_disabled_tot(self): return to_days(
            max(today,self.last_pay.next_disable) -
            self.last_pay.perfect_date)

    # Total amount paid
    def paid_at(self, date):
        try: return self.last_pay_at(date).paid_after
        except: return 0
    @cached_property
    def paid(self): return self.last_pay.paid_after
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
    def outstanding_at(self, date): 
        if self.reg_date <= date:
            return self.plan_tot - self.paid_at(date)
        return 0
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

    # Expected payment
    @property
    def ex_paid_TM(self): 
        if not self.is_active_TM: return 0
        if self.is_new_TM: return self.ex_plan_at(TM_end)
        return max(0,
                int((TM_days - self.credit_at(TM_start))/7 + 1)*self.plan_week)
    @property
    def ex_paid_TM_today(self):
        if not self.is_active_TM: return 0
        if self.is_new_TM: return self.ex_plan_at(today)
        days = to_days(today - TM_start)
        return max(0,
                int((days - self.credit_at(TM_start))/7 + 1)*self.plan_week)
    @property
    def ex_paid_LM(self):
        if not self.is_active_LM: return 0
        if self.is_new_LM: return self.ex_plan_at(LM_end)
        return max(0,
                int((LM_days - self.credit_at(LM_start))/7 + 1)*self.plan_week)

    # Expected collection
    @property
    def ex_collect(self):
        return max(self.ex_plan,self.paid)
    @property
    def ex_collect_TM(self):
        return max(self.ex_paid_TM,self.paid_TM)
    @property
    def ex_collect_TM_today(self):
        return max(self.ex_paid_TM_today,self.paid_TM)
    @property
    def ex_collect_LM(self):
        return max(self.ex_paid_LM,self.paid_LM)

    # Repayment ratios
    @property
    def soft_repayR(self): 
        return ratio(self.paid, self.ex_plan)
    @property
    def repayR(self):
        return ratio(self.paid - self.plan_up, self.ex_plan - self.plan_up)
    @property
    def repayR_EOLM(self):
        if self.is_new_TM: return 0
        return (self.paid_EOLM - self.plan_up) / (self.ex_plan_EOLM - self.plan_up)
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
    perfect_date = models.DateTimeField('perfect disable date', null=True)
    paid_after = models.PositiveIntegerField(default=0, null=True)
    paid_left = models.PositiveIntegerField(default=0, null=True)
    is_last = models.NullBooleanField()
    is_upfront = models.NullBooleanField()
    # manager
    objects = PaymentQuerySet.as_manager()

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))

    # Returns True if the payment was collected this month
    @property
    def is_TM(self): return is_this_month(self.date,0)
    @property
    def is_LM(self): return is_this_month(self.date,-1)

    # Returns the value in days of credit for a "normal" payment
    @property
    def days_value(self): return (self.amount/self.account.plan_week) * 7
    # Returns the value in days of credit of a payment for a deposit
    @property
    def days_value_up(self): 
        return ((self.amount - self.account.plan_up)
                / self.account.plan_week + 1) * 7

# UPDATES FIELDS WHEN A PAYMENT IS CREATED
@receiver(post_save, sender=Payment,
        dispatch_uid='Payment_save_signal')
def record_payment(sender, instance, created, *args, **kwargs):
    if created:
        payments = (instance.account.payments.filter(date__lt = instance.date)
                .order_by('date'))

        if not payments:
            instance.credit_before = 0
            instance.paid_after = instance.amount
            if instance.account.plan_iscash:
                instance.next_disable = instance.date
            else:
                instance.next_disable = instance.date + datetime.timedelta(
                        days=instance.days_value_up)
            instance.perfect_date = instance.next_disable
            instance.is_upfront = True

        else:
            last_pay = payments[0]
            instance.credit_before = to_days(
                    last_pay.next_disable - instance.date)
            instance.paid_after = last_pay.paid_after + instance.amount
            instance.next_disable = (max(instance.date, last_pay.next_disable) 
                    + datetime.timedelta(days=instance.days_value))
            instance.perfect_date = (last_pay.perfect_date
                    + datetime.timedelta(days=instance.days_value))
            last_pay.is_last = False
            last_pay.save()
            instance.is_upfront = False

        instance.paid_left = instance.account.plan_tot - instance.paid_after

        if instance.paid_left == 0:
            instance.account.unlock_date = instance.date
            instance.account.save()

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
            if dec!= 0:
                return str((int(round(top/bottom,2+dec)*math.pow(10,dec+2))
                        /math.pow(10,dec))) + "%"
            return str(int(round(top/bottom,2)*100)) + "%"
        else:
            if dec != 0:
                return str("{:,}".format(int(round(top/bottom,dec)
                    *math.pow(10,dec))/math.pow(10,dec)))
            return str("{:,}".format(int(round(top/bottom,0))))
