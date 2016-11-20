from django.db import models
import datetime, pytz

today = datetime.datetime.today().replace(tzinfo=pytz.utc)

class Update(models.Model):
    date = models.DateTimeField('update date')
    is_full = models.BooleanField()
    hours = models.FloatField(default=0)
    new_clients = models.IntegerField(default=0)
    new_accs = models.IntegerField(default=0)
    new_pays = models.IntegerField(default=0)
   
    @property
    def hours_since(self):
        delta = today - self.date
        return (delta.days * 24) + (delta.seconds / 3600)
