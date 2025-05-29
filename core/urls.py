from django.urls import path
from .views import RegisterCustomerView,CheckEligibilityView

urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register-customer'),
    
    path('check-eligibility', CheckEligibilityView.as_view()),
]
