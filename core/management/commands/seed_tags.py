from django.core.management.base import BaseCommand
from core.models import Tag

class Command(BaseCommand):
    help = "Seed initial tags"

    def handle(self, *args, **kwargs):
        tags = [
            # Core Styles
            "Digital Art",
            "Illustration",
            "Realism",
            "Cartoon",
            "Anime",
            "Semi-Realistic",
            "Pixel Art",
            "Vector Art",
            "3D Art",
            "Concept Art",

            # Character / Subject
            "Character Design",
            "Portrait",
            "Fan Art",
            "OC",
            "Game Art",
            "Fantasy Art",
            "Sci-Fi Art",
            "Creature Design",

            # Use-case
            "Logo Design",
            "Branding",
        ]

        created_count = 0

        for tag_name in tags:
            obj, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created_count} tags created (duplicates skipped)"
        ))

# python manage.py seed_tags