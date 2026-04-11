# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('all-request/', request_view, name='all_request'),
    path('create-request/', add_new_request, name='create_request'),
]