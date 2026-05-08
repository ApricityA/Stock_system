"""
URL configuration for stock_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from stocks.views_pages import dashboard, review, own_stock

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
    path('', dashboard, name='dashboard'),
    path('review/', review, name='review'),
    path('own-stock/', own_stock, name='own_stock'),
]
