# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Phone'
        db.create_table(u'board_phone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('date_of_addition', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('agent', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'board', ['Phone'])

        # Adding M2M table for field advert on 'Phone'
        m2m_table_name = db.shorten_name(u'board_phone_advert')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('phone', models.ForeignKey(orm[u'board.phone'], null=False)),
            ('advert', models.ForeignKey(orm[u'board.advert'], null=False))
        ))
        db.create_unique(m2m_table_name, ['phone_id', 'advert_id'])

        # Adding model 'City'
        db.create_table(u'board_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'board', ['City'])

        # Adding model 'AdminSublocality'
        db.create_table(u'board_adminsublocality', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.City'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'board', ['AdminSublocality'])

        # Adding model 'NonAdminSublocality'
        db.create_table(u'board_nonadminsublocality', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.City'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'board', ['NonAdminSublocality'])

        # Adding model 'Metro'
        db.create_table(u'board_metro', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.City'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'board', ['Metro'])

        # Adding model 'Street'
        db.create_table(u'board_street', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.City'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'board', ['Street'])

        # Adding model 'ObjectType'
        db.create_table(u'board_objecttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'board', ['ObjectType'])

        # Adding model 'Category'
        db.create_table(u'board_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.Category'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('seo_text', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal(u'board', ['Category'])

        # Adding model 'Photo'
        db.create_table(u'board_photo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('advert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.Advert'])),
            ('alt', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
        ))
        db.send_create_signal(u'board', ['Photo'])

        # Adding model 'Advert'
        db.create_table(u'board_advert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.Category'], null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.SmallIntegerField')(default=1, max_length=5, null=True, blank=True)),
            ('metro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.Metro'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_of_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('main_text', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.City'], null=True, blank=True)),
            ('admin_sublocality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.AdminSublocality'], null=True, blank=True)),
            ('non_admin_sublocality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.NonAdminSublocality'], null=True, blank=True)),
            ('object_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['board.ObjectType'], null=True, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('raw_phones', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('seller', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
        ))
        db.send_create_signal(u'board', ['Advert'])

        # Adding model 'ExtraFlat'
        db.create_table(u'board_extraflat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('advert', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['board.Advert'], unique=True)),
            ('rooms_number', self.gf('django.db.models.fields.SmallIntegerField')(max_length=2, null=True, blank=True)),
            ('new_building', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('total_area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('floor', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('floors', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
        ))
        db.send_create_signal(u'board', ['ExtraFlat'])

        # Adding model 'ExtraHouse'
        db.create_table(u'board_extrahouse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('advert', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['board.Advert'], unique=True)),
            ('total_area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lot_area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lot_unit', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('floors', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('gaz', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('water', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('electricity', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
        ))
        db.send_create_signal(u'board', ['ExtraHouse'])

        # Adding model 'ExtraLot'
        db.create_table(u'board_extralot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('advert', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['board.Advert'], unique=True)),
            ('lot_area', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lot_unit', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('intended_purpose', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('gaz', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('water', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('electricity', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
        ))
        db.send_create_signal(u'board', ['ExtraLot'])

        # Adding model 'ExtraRent'
        db.create_table(u'board_extrarent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('advert', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['board.Advert'], unique=True)),
            ('term', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'board', ['ExtraRent'])

        # Adding model 'ExtraSale'
        db.create_table(u'board_extrasale', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('advert', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['board.Advert'], unique=True)),
            ('price_unit', self.gf('django.db.models.fields.SmallIntegerField')(max_length=10, blank=True)),
        ))
        db.send_create_signal(u'board', ['ExtraSale'])


    def backwards(self, orm):
        # Deleting model 'Phone'
        db.delete_table(u'board_phone')

        # Removing M2M table for field advert on 'Phone'
        db.delete_table(db.shorten_name(u'board_phone_advert'))

        # Deleting model 'City'
        db.delete_table(u'board_city')

        # Deleting model 'AdminSublocality'
        db.delete_table(u'board_adminsublocality')

        # Deleting model 'NonAdminSublocality'
        db.delete_table(u'board_nonadminsublocality')

        # Deleting model 'Metro'
        db.delete_table(u'board_metro')

        # Deleting model 'Street'
        db.delete_table(u'board_street')

        # Deleting model 'ObjectType'
        db.delete_table(u'board_objecttype')

        # Deleting model 'Category'
        db.delete_table(u'board_category')

        # Deleting model 'Photo'
        db.delete_table(u'board_photo')

        # Deleting model 'Advert'
        db.delete_table(u'board_advert')

        # Deleting model 'ExtraFlat'
        db.delete_table(u'board_extraflat')

        # Deleting model 'ExtraHouse'
        db.delete_table(u'board_extrahouse')

        # Deleting model 'ExtraLot'
        db.delete_table(u'board_extralot')

        # Deleting model 'ExtraRent'
        db.delete_table(u'board_extrarent')

        # Deleting model 'ExtraSale'
        db.delete_table(u'board_extrasale')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'board.adminsublocality': {
            'Meta': {'ordering': "['name']", 'object_name': 'AdminSublocality'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'board.advert': {
            'Meta': {'object_name': 'Advert'},
            'admin_sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.AdminSublocality']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']", 'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'date_of_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'main_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'metro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Metro']", 'null': 'True', 'blank': 'True'}),
            'non_admin_sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.NonAdminSublocality']", 'null': 'True', 'blank': 'True'}),
            'object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.ObjectType']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'raw_phones': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'seller': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'board.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']", 'null': 'True', 'blank': 'True'}),
            'seo_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'board.city': {
            'Meta': {'object_name': 'City'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'board.extraflat': {
            'Meta': {'object_name': 'ExtraFlat'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'floors': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_building': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'rooms_number': ('django.db.models.fields.SmallIntegerField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'total_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'board.extrahouse': {
            'Meta': {'object_name': 'ExtraHouse'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'electricity': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'floors': ('django.db.models.fields.SmallIntegerField', [], {}),
            'gaz': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lot_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lot_unit': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'total_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'water': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        u'board.extralot': {
            'Meta': {'object_name': 'ExtraLot'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            'electricity': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'gaz': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_purpose': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'lot_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lot_unit': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'water': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        u'board.extrarent': {
            'Meta': {'object_name': 'ExtraRent'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'board.extrasale': {
            'Meta': {'object_name': 'ExtraSale'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price_unit': ('django.db.models.fields.SmallIntegerField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'board.metro': {
            'Meta': {'ordering': "['name']", 'object_name': 'Metro'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'board.nonadminsublocality': {
            'Meta': {'ordering': "['name']", 'object_name': 'NonAdminSublocality'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'board.objecttype': {
            'Meta': {'object_name': 'ObjectType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'board.phone': {
            'Meta': {'object_name': 'Phone'},
            'advert': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['board.Advert']", 'null': 'True', 'blank': 'True'}),
            'agent': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_addition': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'board.photo': {
            'Meta': {'object_name': 'Photo'},
            'advert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Advert']"}),
            'alt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'board.street': {
            'Meta': {'ordering': "['name']", 'object_name': 'Street'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['board']