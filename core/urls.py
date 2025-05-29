from django.urls import path
from .views import RegisterCustomerView,test_route

urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register-customer'),
    path('test', test_route)
]
