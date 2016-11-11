# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'GallaryModel.preview'
        db.alter_column(u'lukomorye_gallarymodel', 'preview', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))

    def backwards(self, orm):

        # Changing field 'GallaryModel.preview'
        db.alter_column(u'lukomorye_gallarymodel', 'preview', self.gf('django.db.models.fields.files.ImageField')(default='ff', max_length=100))

    models = {
        u'lukomorye.gallarymodel': {
            'Meta': {'object_name': 'GallaryModel'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lukomorye']