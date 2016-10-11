from django.db import models
# Imports to handle dates and timezones
import datetime, calendar, pytz
# Some models from the sales app are imported in inventory.models which can
# create a circular import error
from inventory.models import Product, Warehouse

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

    def __str__(self):
        return ('%s (%s)' % (self.name, self.location))

    # Returns the earliest registration date
    @property
    def get_from(self):
        result = datetime.datetime.today().replace(tzinfo=pytz.utc)
        for acc in Account.objects.filter(client=self):
            result = min(acc.reg_date,result)
        return result

    # Returns True if the client was created a given month offset from today
    def new_TM(self,offset):
        return thisMonth(self.get_from,offset)

    # Returns true if the client was created this month
    @property
    def get_new_TM(self):
        return self.new_TM(0)

    # Returns true if the client was created last month
    @property
    def get_new_LM(self):
        return self.new_TM(-1)

# MANAGER CLASS, RESPONSIBLE FOR SEVERAL AGENTS
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

    # Returns the monthly expected collection for an agent
    @property
    def get_collect_expected_TM(self):
        Q = [obj for obj in Account.objects.filter(agent = self)
                if obj.get_isActive_TM]
        result = 0
        for account in Q:
            result += (account.get_paid_expected_TM 
                    - min(0,account.get_pay_deficit))
        return result

    # Returns the collection % covered by this month's upfront payments
    @property
    def get_collect_upfront(self):
        Q = [obj for obj in Account.objects.filter(agent = self)
                if obj.get_isActive_TM]
        paid_up = 0
        for account in Q:
            if thisMonth(account.reg_date,0):
                paid_up += account.plan_up
        try: 
            return int(round(paid_up/self.get_collect_expected_TM*100,0))
        except:
            return str(0)

    # Returns the collection % covered by this month's recurring payments
    @property
    def get_collect_rec(self):
        Q = [obj for obj in Account.objects.filter(agent = self)
                if obj.get_isActive_TM]
        paid_rec = 0
        for account in Q:
            if thisMonth(account.reg_date,0):
                paid_rec += account.get_paid_TM - account.plan_up
            else:
                paid_rec += account.get_paid_TM
        try: 
            return int(round(paid_rec/self.get_collect_expected_TM*100,0))
        except:
            return str(0)

    # Returns the collection % of late payments
    @property
    def get_collect_late(self):
        Q = [obj for obj in Account.objects.filter(agent = self)
                if obj.get_isActive_TM]
        paid_late = 0
        for account in Q:
            paid_late += max(0,account.get_pay_deficit)
        try: 
            return int(round(paid_late/self.get_collect_expected_TM*100,0))
        except:
            return str(0)

# SIMPLE ACCOUNT CLASS WITH PLENTY OF FUNCTIONS FOR ANALYTICS
# By convention, all @property methods are named get_ to not be confused with
# class attributes
# Model doesn't work yet with detached (reposessed) and replaced lamps
# Also, test accounts are not taken into account at this stage
# Could actually override save to make sure that origin inventory gets updated
# automatically
# PLAN is not a separate class because of how plans can change over time and
# it would be a nightmare to track (they keep the same name on the hub)
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

    # Total payments collected
    @property
    def get_paid(self):
        result = 0
        for payment in Payment.objects.filter(account = self):
            result += payment.amount
        return result

    # Payments collected a given month, 'offset' from current month
    def paid_TM(self, offset):
        result = 0
        today = datetime.datetime.today()
        _today = add_months(today,offset).replace(tzinfo=pytz.utc)
        for payment in Payment.objects.filter(account = self): 
            if (payment.date.year == _today.year and 
                    payment.date.month == _today.month):
                result += payment.amount
        return result

    # Payments collected this month
    # Made a property for ease of use in templates
    @property
    def get_paid_TM(self):
        return self.paid_TM(0)

    # Payments collected last month
    # Made a property for ease of use in templates
    @property
    def get_paid_LM(self):
        return self.paid_TM(-1)

    # Total number of payments
    @property
    def get_pay_nb(self):
        return Payment.objects.filter(account = self).count()

    # Number of payments for a given month, 'offset' from current month
    def pay_nb_TM(self, offset):
        result = 0
        today = datetime.datetime.today()
        _today = add_months(today,offset).replace(tzinfo=pytz.utc)
        for payment in Payment.objects.filter(account = self): 
            if (payment.date.year == _today.year and 
                    payment.date.month == _today.month):
                result += 1
        return result

    # Number of payments this month
    # Made a property for ease of use in templates
    @property
    def get_pay_nb_TM(self):
        return self.pay_nb_TM(0)

    # Number of payments last month
    # Made a property for ease of use in templates
    @property
    def get_pay_nb_LM(self):
        return self.pay_nb_LM(-1)

    # Expected payment as of 'date'
    def paid_expected(self, date):
        if date < self.reg_date:
            return 0
        delta = date - self.reg_date
        full_weeks = int(toWeeks(delta))
        return min(self.plan_up + self.plan_week*full_weeks, 
                self.plan_tot)

    # Expected payment as of today
    # Made a property for ease of use in templates
    @property
    def get_paid_expected(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        return self.paid_expected(today)

    # Expected payment as of end of month
    # Made a property for ease of use in templates
    @property
    def get_paid_expected_TM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eom = monthEnd(today)
        return self.paid_expected(eom)

    # Expected payment as of end of last month
    # Made a property for ease of use in templates
    @property
    def get_paid_expected_LM(self):
        today = datetime.datetime.today().replace(tzinfo=pytz.utc)
        eolm = monthEnd(addmonth(today,-1))
        return self.paid_expected(eolm)

    # Returns True if the account was created a given month offset from today
    def new_TM(self,offset):
        return thisMonth(self.reg_date,offset)

    # Returns true if the client was created this month
    @property
    def get_new_TM(self):
        return self.new_TM(0)

    # Returns true if the client was created last month
    @property
    def get_new_LM(self):
        return self.new_TM(-1)

    # Payment deficit, can be negative if in advance
    @property
    def get_pay_deficit(self):
        return self.get_paid_expected - self.get_paid

    # Projected payment deficit at end of month
    @property
    def get_pay_deficit_TM(self):
        return self.get_paid_expected_TM - self.get_paid_TM

    # Payment deficit at end of last month
    @property
    def get_pay_deficit_LM(self):
        return self.get_paid_expected_LM - self.get_paid_LM

    # Returns a Payment object with the last payment
    @property
    def get_lastPay(self):
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
    
    # Current disabled, made into a property for use in templates
    @property
    def get_current_disabled(self):
        return self.days_disabled(now=True)

    # False if account is not active this month
    @property
    def get_isActive_TM(self):
        return (
                (self.status == 'e') 
                or (self.status == 'd')
                or (self.status == 'u' and thisMonth(self.get_lastPay.date,0)) 
                )

    # Returns outstanding amount for which no payments in the last 'days'
    def OAR(self,days):
        if self.days_disabled(now=True) > days:
            return self.plan_tot - self.get_paid
        return 0

# SIMPLE PAYMENT CLASS, INCLUDES ANGAZA ID TO USE AS PRIMARY KEY WHEN UPDATING
class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField('payment date')
    agent = models.ForeignKey(Agent)
    id_Angaza = models.CharField(max_length=8, null=True)

    def __str__(self):
        return ('%s (%s)' % (str(self.amount), self.account))

    # Returns True if the account was collected this month
    @property
    def get_TM(self):
        return thisMonth(self.date,0)

    # Returns True if the account was collected last month
    @property
    def get_LM(self):
        return thisMonth(self.date,-1)

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
def toWeeks(delta):
    result = delta.days/7
    result += delta.seconds/7/(3600*24)
    result += delta.microseconds/7/(3600*24)/1000000
    return result

# Return the last second of the last day of the month of a given date
def monthEnd(date):
    result = datetime.datetime(date.year, date.month+1, 1,
            00,00,00,000000).replace(tzinfo=pytz.utc)
    return result - datetime.timedelta(0,1,0)

# Returns Yes if date is of today's month with offset
def thisMonth(date,offset):
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)
    return (date > monthEnd(add_months(today,-1+offset)) and
        date <= monthEnd(add_months(today,offset)))
