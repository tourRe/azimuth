from django.conf.urls import url
from . import views

app_name = 'sales'
urlpatterns = [
        url(r'^$', 
            views.index, name='index'),
        url(r'^(?P<manager_firstname>[A-Za-z _]+)/$', 
            views.manager, name='manager'),
        url(r'^(?P<agent_login>[A-Za-z _.]+)/$', 
            views.agent, name='agent'),
        ]
