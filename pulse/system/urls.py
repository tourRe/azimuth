from django.conf.urls import url
from . import views

OPTION = r'(?P<option>[^/]+)/'

app_name = 'system'
urlpattenrs = [
        url(r'^collect/$', views.collect, name='collect'),
        url(r'^collect/' + OPTION + '$', views.collect, name='collect'),
]
