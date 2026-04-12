import uuid
from django.db import models
from commissions.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'       # created, not paid
        HELD = 'held'             # escrow (money received)
        RELEASED = 'released'     # paid to artist
        REFUNDED = 'refunded'     # returned to client
        FAILED = 'failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField('commissions.Order', on_delete=models.CASCADE, related_name='payment')
    
    amount = models.IntegerField()

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    provider = models.CharField(max_length=50)  
    provider_payment_id = models.CharField(max_length=255, blank=True)

    released_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    # Optional but useful
    provider_order_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)