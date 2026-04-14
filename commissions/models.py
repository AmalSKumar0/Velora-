import uuid
from django.db import models
from django.conf import settings
from users.models import ArtistProfile
from core.models import Tag
from django.core.validators import MinValueValidator, MaxValueValidator


class Request(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'                     # accepting proposals
        IN_PROGRESS = 'in_progress', 'In Progress' # artist selected, order created
        COMPLETED = 'completed', 'Completed'       # order finished successfully
        CANCELLED = 'cancelled', 'Cancelled'       # client cancelled before completion
        EXPIRED = 'expired', 'Expired'             # no proposals / timeout

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget_min = models.IntegerField()
    budget_max = models.IntegerField()

    tags = models.ManyToManyField(Tag, related_name='requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)


class RequestImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='request_images/')

class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='proposals')
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='proposals')

    price = models.IntegerField()
    message = models.TextField()
    delivery_days = models.IntegerField()

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'artist')
    
class Order(models.Model):
    class Status(models.TextChoices):
        PAYMENT_PENDING = 'payment_pending'
        IN_PROGRESS = 'in_progress'
        SUBMITTED = 'submitted'
        REVISION_REQUESTED = 'revision_requested'
        APPROVED = 'approved'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'
        DISPUTED = 'disputed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='artist_orders')
    amount = models.IntegerField()
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PAYMENT_PENDING
    )
    revision_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='submissions')
    
    version = models.IntegerField()
    
    preview_file = models.FileField(upload_to='order_files/previews/')
    original_file = models.FileField(upload_to='order_files/originals/')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("order", "version")
        ordering = ["-version"]


class SubmissionReview(models.Model):
    class Action(models.TextChoices):
        APPROVED = "approved"
        CHANGES_REQUESTED = "changes_requested"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    action = models.CharField(max_length=20, choices=Action.choices)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class OrderUpdate(models.Model):

    message = models.TextField(blank=True)

    submission = models.ForeignKey(
        Submission,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE)

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



class Dispute(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open'
        RESOLVED = 'resolved'
        REJECTED = 'rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)