# urls.py
from django.urls import path
from .views import *

urlpatterns = [
   path('pay-order/<uuid:order_id>',create_payment,name='create_payment'),
   path('verify/',verify_payment)
]