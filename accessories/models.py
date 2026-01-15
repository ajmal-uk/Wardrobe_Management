from django.db import models
from accounts.models import CustomUser
from wardrobe.models import Occasion, Season
from .utils import extract_dominant_color   # 🔹 IMPORTANT IMPORT


class Accessory(models.Model):
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)


    color = models.CharField(max_length=50, null=True, blank=True)

    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)

    image = models.ImageField(upload_to='accessories/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

 
        if self.image and not self.color:
            self.color = extract_dominant_color(self.image.path)
            super().save(update_fields=['color'])

    def __str__(self):
        return self.name
