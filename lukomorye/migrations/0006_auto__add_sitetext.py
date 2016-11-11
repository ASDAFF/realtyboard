# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteText'
        db.create_table(u'lukomorye_sitetext', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text1', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'lukomorye', ['SiteText'])


    def backwards(self, orm):
        # Deleting model 'SiteText'
        db.delete_table(u'lukomorye_sitetext')


    models = {
        u'lukomorye.gallarymodel': {
            'Meta': {'object_name': 'GallaryModel'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'lukomorye.sitetext': {
            'Meta': {'object_name': 'SiteText'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text1': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['lukomorye']