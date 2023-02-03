"""shield URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from api.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', login),
    path('fb_login', login_firebase),
    path('create', create_user),
    path('store', StoreListView.as_view()),
    path('store/<int:id>', CookiesListView.as_view()),
    path('cookies', CookiesListView.as_view()),
    path('cookies/<int:id>', CookiesUpdateView.as_view()),
    path('request', RequestListView.as_view()),
    path('request/<int:id>', RequestUpdateView.as_view()),
    path('car', CarListView.as_view()),
    path('car/choose', set_car),
    path('car/update', DeliveryUpdateView.as_view()),
    path('delivery', DeliveryList.as_view()),
]
