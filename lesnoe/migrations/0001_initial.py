# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gallery'
        db.create_table(u'lesnoe_gallery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('picture', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.CharField')(max_length=110, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('sort', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'lesnoe', ['Gallery'])


    def backwards(self, orm):
        # Deleting model 'Gallery'
        db.delete_table(u'lesnoe_gallery')


    models = {
        u'lesnoe.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sort': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '110', 'blank': 'True'})
        }
    }

    complete_apps = ['lesnoe']