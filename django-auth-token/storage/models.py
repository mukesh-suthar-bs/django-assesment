from django.db import models
from django.contrib.auth.models import User


class ImageFile(models.Model):
    parent_type = models.CharField(max_length=255, blank=False, null=False)
    parent_id = models.IntegerField(blank=False, null=False)
    image = models.ImageField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
