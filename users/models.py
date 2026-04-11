import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Tag


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        ARTIST = 'artist', 'Artist'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=Role.choices)

    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class ArtistProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')

    display_name = models.CharField(max_length=255)
    
    bio = models.TextField(blank=True)

    portfolioURL = models.URLField()

    tags = models.ManyToManyField(Tag, related_name='artist')

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name


class PortfolioItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='portfolio')

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True)

    tags = models.ManyToManyField(Tag, related_name='portfolio_items')

    created_at = models.DateTimeField(auto_now_add=True)