from django.db import models
import datetime, pytz

today = datetime.datetime.today().replace(tzinfo=pytz.utc)

class UpdateQuerySet(models.QuerySet):

    def last_update(self):
        return self.order_by('date').reverse()[0]

    def last_full_update(self):
        return self.filter(is_full = True).order_by('date').reverse()[0]

class Update(models.Model):
    date = models.DateTimeField('update date')
    is_full = models.BooleanField()
    hours = models.FloatField(default=0)
    new_clients = models.IntegerField(default=0)
    new_accs = models.IntegerField(default=0)
    new_pays = models.IntegerField(default=0)
    objects = UpdateQuerySet.as_manager()
   
    def __str__(self):
        return ('%s - Is Full = %s' % (str(self.date), str(self.is_full)))

    @property
    def hours_since(self):
        delta = today - self.date
        return (delta.days * 24) + (delta.seconds / 3600)
