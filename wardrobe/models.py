from django.db import models
from accounts.models import CustomUser
from .utils import extract_dominant_color


class Occasion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class WardrobeItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    item_type = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    color = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='wardrobe/', null=True, blank=True)

    wear_count = models.PositiveIntegerField(default=0)
    clean_status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if self.image and (not self.color or is_new):
            self.color = extract_dominant_color(self.image.path)
            super().save(update_fields=['color'])

    def mark_worn(self):
        self.wear_count += 1

        category_name = self.category.name.strip().lower()

        # TOP → dirty after 1 wear
        if category_name == 'top' and self.wear_count >= 1:
            self.clean_status = False

        # BOTTOM → dirty after 3 wears
        elif category_name == 'bottom' and self.wear_count >= 3:
            self.clean_status = False

        self.save()

    def __str__(self):
        return self.item_type
