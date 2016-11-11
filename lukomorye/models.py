from django.db import models
from PIL import Image

class GallaryModel(models.Model):
    photo = models.ImageField(upload_to='lukomorye')
    preview = models.ImageField(upload_to='lukomorye/thumbs', blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    place = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.photo.url
    
    # def save(self, *args, **kwargs):
    #     return super(GallaryModel, self).save()
    

class SiteText(models.Model):
    text1 = models.TextField()