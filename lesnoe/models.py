# -*- coding: utf-8 -*-
from ckeditor.fields import RichTextField
from django.db import models


class Gallery(models.Model):
    picture = models.ImageField(upload_to='lesnoe/gallery')
    thumbnail = models.ImageField(upload_to='lesnoe/gallery/thumb', blank=True, null=True)
    description = models.CharField(max_length=350, blank=True)
    sort = models.FloatField(blank=True, null=True)
    
    class Meta:
        ordering = ['sort']

class Project(models.Model):
    place_in_line = models.IntegerField(default=0)
    area_living = models.FloatField(default=0)
    area_total = models.FloatField(default=0)
    area_garage = models.FloatField(default=0)
    area_2nd_fl = models.FloatField(default=0)
    volume = models.FloatField(default=0)
    height = models.FloatField(default=0)
    roof_angle = models.IntegerField()
    min_plot_width = models.FloatField(default=0)
    min_plot_length = models.FloatField(default=0)
    house_price = models.IntegerField(default=0)
    project_price = models.IntegerField(default=0)
    description = models.CharField(max_length=300)
    z500_id = models.CharField(max_length=6)

    def get_main_img(self):
        pic = self.projectimg_set.filter(main=True)[:1]
        if not pic:
            pic = self.projectimg_set.all()[:1]
        return pic[0].picture.url
    
    def get_next_id(self):
        projs = Project.objects.all().order_by('id')
        if self.id < len(projs):
            for i, proj in enumerate(projs):
                if proj.id == self.id:
                    return projs[i+1].id
        else: 
            return None
                
    def get_previous_id(self):
        projs = Project.objects.all().order_by('id')
        for i, proj in enumerate(projs):
            if proj.id == self.id and i > 0:
                return projs[i-1].id
        else: 
            return None
        

class ProjectImg(models.Model):
    project = models.ForeignKey(Project)
    picture = models.ImageField(upload_to='lesnoe/projects')
    description = models.CharField(max_length=200, blank=True)
    main = models.BooleanField(default=False)
    
    
class PageText(models.Model):
    name = models.CharField(max_length=20, default=u"текст страницы")
    text1 = RichTextField()
    
    def __unicode__(self):
        return self.name
    