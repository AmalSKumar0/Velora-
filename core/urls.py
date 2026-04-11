# urls.py
from django.urls import path
from .views import tag_list_create, tag_update, tag_delete

urlpatterns = [
    path("tags/", tag_list_create, name="tag_list"),
    path("tags/edit/<int:tag_id>/", tag_update, name="tag_update"),
    path("tags/delete/<int:tag_id>/", tag_delete, name="tag_delete"),
]