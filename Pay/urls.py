from django.contrib import admin
from django.urls import path
from Payment import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', views.register),
    path('wallet/', views.wallet),
    path('add_money/', views.add_money),
    path('send_money/', views.send_money),
    path('transactions/', views.transactions),
]