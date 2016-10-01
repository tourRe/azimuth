from django.conf.urls import url
from . import views

app_name = 'sales'
urlpatterns = [
        url(r'^$', 
            views.index, name='index'),
        url(r'^managers/$', 
            views.manager_index, name='manager_index'),
        url(r'^managers/(?P<manager_firstname>[A-Za-z _]+)/$', 
            views.manager, name='manager'),
        url(r'^agents/$', 
            views.agent_index, name='agent_index'),
        url(r'^agents/(?P<agent_login>[A-Za-z _.]+)/$', 
            views.agent, name='agent'),
        url(r'^clients/$', 
            views.client_index, name='client_index'),
        url(r'^clients/(?P<client_pk>[0-9]+)/$', 
            views.client, name='client'),
        url(r'^accounts/$', 
            views.account_index, name='account_index'),
        url(r'^accounts/(?P<account_Angaza>[A-Za-z0-9]+)/$', 
            views.account, name='account'),
        url(r'^payments/$', 
            views.payment_index, name='payment_index'),
        ]
