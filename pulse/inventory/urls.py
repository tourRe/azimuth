from django.conf.urls import url
from . import views

app_name = 'inventory'
urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^confirmation/$', 
                views.confirmation, name='confirmation'),
            url(r'^(?P<warehouse_name>[A-Za-z _]+)/$', 
                views.warehouse, name='warehouse'),
            ]
