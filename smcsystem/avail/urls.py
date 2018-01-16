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
from avail import views
urlpatterns = [
    url(r'^create', views.create, name="create"),
    url(r'^chart/xm_chart', views.xm_chart, name="xm_chart"),
    url(r'^chart/gz_chart', views.gz_chart, name="gz_chart"),
    url(r'^gz_chart', views.gz_index, name="gz_index"),
    url(r'^year_chart', views.year_chart, name="year_chart"),
    url(r'^chart', views.avail_index, name="avail_index"),
    url(r'^settings', views.settings_index, name="settings_index"),


]
