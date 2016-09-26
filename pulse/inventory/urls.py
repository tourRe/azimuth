from django.conf.urls import url
from . import views

app_name = 'inventory'
urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^(?P<warehouse_name>[A-Za-z ]+)/$', views.warehouse, name='warehouse'),
            url(r'^(?P<warehouse_name>[A-Za-z ]+)/transaction/$', views.transaction, name='transaction'),
            url(r'^(?P<warehouse_name>[A-Za-z ]+)/transfer/$', views.warehouse, name='transfer'),
            ]
