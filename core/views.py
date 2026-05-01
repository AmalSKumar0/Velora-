import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tag
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from django.http import HttpResponse
from django.contrib import messages

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


@login_required
@role_required('admin')
def tag_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tags.csv"'

    writer = csv.writer(response)
    writer.writerow(['name'])

    tags = Tag.objects.all().values_list('name', flat=True)
    for tag_name in tags:
        writer.writerow([tag_name])

    return response

@login_required
@role_required('admin')
def tag_import_csv(request):
    if request.method == "POST" and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a valid CSV file.')
            return redirect('tag_list')

        try:
            file_data = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(file_data)
            next(reader, None)  # Skip header

            created_count = 0
            for row in reader:
                if row:
                    name = row[0].strip()
                    if name:
                        obj, created = Tag.objects.get_or_create(name=name)
                        if created:
                            created_count += 1

            messages.success(request, f'Successfully imported {created_count} tags.')
        except Exception as e:
            messages.error(request, f'Error importing CSV: {str(e)}')

    return redirect('tag_list')