# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Advert.author'
        db.alter_column(u'board_advert', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.MyUser'], null=True))

        # Changing field 'Phone.owner'
        db.alter_column(u'board_phone', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.MyUser'], null=True))

    def backwards(self, orm):

        # Changing field 'Advert.author'
        db.alter_column(u'board_advert', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

        # Changing field 'Phone.owner'
        db.alter_column(u'board_phone', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

    models = {
        u'board.advert': {
            'Meta': {'object_name': 'Advert'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.MyUser']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']"}),
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
            'price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'raw_phones': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'seller': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Sublocality']", 'null': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'board.extracommercial': {
            'Meta': {'object_name': 'ExtraCommercial'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.ObjectType']", 'null': 'True', 'blank': 'True'})
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.MyUser']", 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'board.photo': {
            'Meta': {'object_name': 'Photo'},
            'advert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Advert']"}),
            'alt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'board.street': {
            'Meta': {'ordering': "['name']", 'object_name': 'Street'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'board.sublocality': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sublocality'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'personal.myuser': {
            'Meta': {'object_name': 'MyUser'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['board']