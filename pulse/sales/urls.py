from django.conf.urls import url
from . import views

# defining common REGEX expressions
AGENT = r'(?P<agent>[^/]+)/'


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
        url(r'^agents/(?P<agent_login>[A-Za-z0-9 _.]+)/$', 
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

        url(r'^payments/graph/season_hour/$',
            views.payment_season_hour, name='pay_seas_hour'),
        url(r'^payments/graph/season_day/$',
            views.payment_season_day, name='pay_seas_day'),

        url(r'^payments/graph/volume_week/$',
            views.payment_volume_weekly, name='pay_vol_week'),
        url(r'^payments/graph/volume_week/' + AGENT + '$',
            views.payment_volume_weekly, name='pay_vol_week'),

        url(r'^payments/graph/number_week/$',
            views.payment_number_weekly, name='pay_num_week'),
        url(r'^payments/graph/number_week/' + AGENT + '$',
            views.payment_number_weekly, name='pay_num_week'),

        url(r'^accounts/graph/new_week/$',
            views.account_new_week, name='acc_new_week'),
        url(r'^accounts/graph/new_week/' + AGENT + '$',
            views.account_new_week, name='acc_new_week'),

        url(r'^accounts/graph/rev_week/$',
            views.revenue_new_week, name='rev_new_week'),
        url(r'^accounts/graph/rev_week/' + AGENT + '$',
            views.revenue_new_week, name='rev_new_week'),

        url(r'^accounts/graph/number_by_disable/$',
            views.account_number_by_disable, name='acc_num_dis'),
        url(r'^accounts/graph/number_by_disable/' + AGENT + '$',
            views.account_number_by_disable, name='acc_num_dis'),

        url(r'^accounts/graph/outstanding_by_disable/$',
            views.account_outstanding_by_disable, name='acc_out_dis'),
        url(r'^accounts/graph/outstanding_by_disable/' + AGENT + '$',
            views.account_outstanding_by_disable, name='acc_out_dis'),
        ]
