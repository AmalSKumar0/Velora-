# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tag
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from users.decorators import role_required


@login_required
@role_required('admin')
def tag_list_create(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Tag.objects.create(name=name)

        return redirect("tag_list")

    tags = Tag.objects.all()
    return render(request, "admin/tag/tags.html", {"tags": tags})


# UPDATE
@login_required
@role_required('admin')
def tag_update(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            tag.name = name
            tag.save()
        return redirect("tag_list")

    return render(request, "admin/tag/tag_update.html", {"tag": tag})


# DELETE
@login_required
@role_required('admin')
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == "POST":
        tag.delete()
        return redirect("tag_list")

    return render(request, "admin/tag/tag_delete.html", {"tag": tag})