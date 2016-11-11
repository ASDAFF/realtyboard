# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'lesnoe_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place_in_line', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('area_living', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('area_total', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('area_garage', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('area_2nd_fl', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('volume', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('height', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('roof_angle', self.gf('django.db.models.fields.IntegerField')()),
            ('min_plot_width', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('min_plot_length', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('house_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('project_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('z500_id', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal(u'lesnoe', ['Project'])

        # Adding model 'ProjectImg'
        db.create_table(u'lesnoe_projectimg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lesnoe.Project'])),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'lesnoe', ['ProjectImg'])


        # Changing field 'Gallery.picture'
        db.alter_column(u'lesnoe_gallery', 'picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

        # Changing field 'Gallery.thumbnail'
        db.alter_column(u'lesnoe_gallery', 'thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))

    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'lesnoe_project')

        # Deleting model 'ProjectImg'
        db.delete_table(u'lesnoe_projectimg')


        # Changing field 'Gallery.picture'
        db.alter_column(u'lesnoe_gallery', 'picture', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Gallery.thumbnail'
        db.alter_column(u'lesnoe_gallery', 'thumbnail', self.gf('django.db.models.fields.CharField')(default='', max_length=110))

    models = {
        u'lesnoe.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'sort': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'lesnoe.project': {
            'Meta': {'object_name': 'Project'},
            'area_2nd_fl': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'area_garage': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'area_living': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'area_total': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'house_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_plot_length': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'min_plot_width': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'place_in_line': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'project_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'roof_angle': ('django.db.models.fields.IntegerField', [], {}),
            'volume': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'z500_id': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        u'lesnoe.projectimg': {
            'Meta': {'object_name': 'ProjectImg'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lesnoe.Project']"})
        }
    }

    complete_apps = ['lesnoe']