from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class JWT(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-user']

    def __str__(self):
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fav_xter = models.JSONField(blank=True, default=dict)
    fave_quotes = models.JSONField(blank=True, default=dict)


    class Meta:
        ordering = ['-user']
    
    def __str__(self):
        return self.user.username