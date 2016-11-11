# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'GallaryModel.name'
        db.delete_column(u'lukomorye_gallarymodel', 'name')

        # Adding field 'GallaryModel.preview'
        db.add_column(u'lukomorye_gallarymodel', 'preview',
                      self.gf('django.db.models.fields.files.ImageField')(default='prev', max_length=100),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'GallaryModel.name'
        db.add_column(u'lukomorye_gallarymodel', 'name',
                      self.gf('django.db.models.fields.CharField')(default='nana', max_length=50),
                      keep_default=False)

        # Deleting field 'GallaryModel.preview'
        db.delete_column(u'lukomorye_gallarymodel', 'preview')


    models = {
        u'lukomorye.gallarymodel': {
            'Meta': {'object_name': 'GallaryModel'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['lukomorye']