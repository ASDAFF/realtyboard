from django.db import models

class TestParser(models.Model):
    name = models.CharField(max_length=25)
    time = creation_date = models.DateTimeField(auto_now_add=True)