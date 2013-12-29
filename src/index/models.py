from django.db import models

# Create your models here.

class Index(models.Model):
    welcome_text = models.CharField(max_length=200)