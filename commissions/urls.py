# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('all-request/', request_view, name='all_request'),
    path('create-request/', add_new_request, name='create_request'),
    path('create-proposal/',send_new_proposal, name='create_proposal'),
    path('view-all-proposal/<uuid:id>',view_all_proposal,name='all_proposals'),
    path('accept-proposal/<uuid:id>',accept_proposal,name='accept_proposal')
]