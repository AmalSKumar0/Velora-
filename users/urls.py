
from django.contrib import admin
from django.urls import path
from .views.admin_views import *
from .views.artist_views import *
from .views.client_views import *


urlpatterns = [
    path('admin-dashboard/',admin_dash,name='adminDashboard'),
    path('client-dashboard/',client_dash,name='clientDashboard'),
    path('artist-dashboard/',artist_dash,name='artistDashboard'),


    path('admin/download-report/', download_admin_report, name='download_report'),

    # admin
    path('admin/all-users/',users_view,name="allusers"),
    path('admin/delete-user/<uuid:id>/',delete_user_view,name="deleteuser"),
    path('admin/requests/', admin_requests, name='admin_requests'),
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('admin/payments/',admin_payments,name="admin_payments"),
    path('admin/delete-request/<uuid:id>/', delete_request_view, name="delete_request"),
    path('admin/delete-order/<uuid:id>/', delete_order_view, name="delete_order"),
    path('admin/delete-payment/<uuid:id>/', delete_payment_view, name="delete_payment"),



    # artists
    path('artist/create-profile/',create_artist_profile,name="create_artist_profile"),
    path('artist/create-portfolio/',add_portfolio_item,name="add_portfolio_item"),
    path('artist/view-works/',view_my_work,name="view_my_work"),
    path('artist/individual-work/<uuid:order_id>',individual_work,name="individual_work"),
    path("artist/profile/",artist_profile_view,name="artist_profile"),
    path('artist/delete_portfolio/<uuid:id>',delete_portfolio_item,name="delete_portfolio_item"),

  

    # client
    path('client/individual-work/<uuid:order_id>',clinet_view_individual_work,name="clinet_view_individual_work"),
    path('client/complete-work/<uuid:order_id>',complete_order,name="complete_order"),
    path("download/<uuid:submission_id>/", download_final, name="download_final"),
    path("review/add-review/",add_review,name="submit_review"),
    path("review/delete/<uuid:id>/",delete_review,name="delete_review"),
    path("review/edit/<uuid:id>/",edit_review,name="edit_review"),
    path("client/profile/",client_profile,name="client_profile"),
    path("client/profileupdate/", update_profile, name='update_profile'),
    path('artist/profile/<str:username>/', public_artist_profile, name='public_artist_profile'),
    path('client/order/<uuid:order_id>/dispute/', raise_dispute, name="raise_dispute"),
]
