
from django.contrib import admin
from django.urls import path
from .views.admin_views import *
from .views.artist_views import *
from .views.client_views import *


urlpatterns = [
    path('admin-dashboard/',admin_dash,name='adminDashboard'),
    path('client-dashboard/',client_dash,name='clientDashboard'),
    path('artist-dashboard/',artist_dash,name='artistDashboard'),


    # admin
    path('admin/all-users/',users_view,name="allusers"),
    path('admin/delete-user/<uuid:id>/',delete_user_view,name="deleteuser"),


    # artists
    path('artist/create-profile/',create_artist_profile,name="create_artist_profile"),
    path('artist/create-portfolio/',add_portfolio_item,name="add_portfolio_item"),
]
