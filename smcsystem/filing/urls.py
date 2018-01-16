"""smcsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from filing import views
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^api/host/', views.Host_api.as_view(),name='hostapi'),
    url(r'^server/log/', views.serverlog,name='serverlog'),
    url(r'^server/errorlog/', views.server_error_log,name='servererrorlog'),
    url(r'^server/disk_chart/', views.disk_chart, name='disk_chart'),
    url(r'^server/mem_chart/', views.mem_chart, name='mem_chart'),
    url(r'^server/cq_chart/', views.cq_chart, name='cq_chart'),
    url(r'^server/app_chart/', views.app_chart, name='app_chart'),
    url(r'^server/group_history/', views.group_history, name='group_history'),
    url(r'^server/car_num_chart/', views.car_num_chart, name='car_num_chart'),
    url(r'^command/operation/', views.command_operation, name='command_operation'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^init/data', views.init_data, name='init_data'),
    url(r'^init/host', views.init_host, name='init_host'),
    url(r'^init/cq_data', views.init_cq_data, name='init_cq_data'),
    url(r'^log/(\w+)/(\w+)/$', views.log_cat, name="log_cat"),
]
