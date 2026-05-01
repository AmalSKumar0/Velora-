# urls.py
from django.urls import path
from .views import tag_list_create, tag_update, tag_delete, tag_export_csv, tag_import_csv

urlpatterns = [
    path("tags/", tag_list_create, name="tag_list"),
    path("tags/edit/<int:tag_id>/", tag_update, name="tag_update"),
    path("tags/delete/<int:tag_id>/", tag_delete, name="tag_delete"),
    path("tags/export/", tag_export_csv, name="tag_export_csv"),
    path("tags/import/", tag_import_csv, name="tag_import_csv"),
]