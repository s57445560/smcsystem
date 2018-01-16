
from django.conf.urls import url, include
from django.contrib import admin
from king_admin import views
urlpatterns = [
    url(r'^(\w+)/(\w+)/$', views.table_obj, name="table_obj"),
    url(r'^(\w+)/(\w+)/(\w+)/change/$', views.table_obj_change, name="table_obj_change"),
    url(r'^(\w+)/(\w+)/(\w+)/delete/$', views.table_obj_delete, name="table_obj_delete"),
    url(r'^(\w+)/(\w+)/add/$', views.table_obj_add, name="table_obj_add"),
]
