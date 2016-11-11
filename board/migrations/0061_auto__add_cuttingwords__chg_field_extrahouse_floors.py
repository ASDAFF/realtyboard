# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'ExtraHouse.floors'
        db.alter_column(u'board_extrahouse', 'floors', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

    def backwards(self, orm):
        # Changing field 'ExtraHouse.floors'
        db.alter_column(u'board_extrahouse', 'floors', self.gf('django.db.models.fields.SmallIntegerField')(default=None))

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
        u'board.advert': {
            'Meta': {'ordering': "['-date_of_update']", 'object_name': 'Advert'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']"}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            'date_of_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'main_text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'metro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Metro']", 'null': 'True', 'blank': 'True'}),
            'price_uah': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price_unit': ('django.db.models.fields.SmallIntegerField', [], {'default': "(1, u'\\u0437\\u0430 \\u043e\\u0431\\u044a\\u0435\\u043a\\u0442')", 'null': 'True'}),
            'price_usd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'raw_phones': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'seller': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'settlement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Settlement']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Sublocality']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '90', 'blank': 'True'}),
            'vparser': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'})
        },
        u'board.adverttodelete': {
            'Meta': {'object_name': 'AdvertToDelete'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            'date_of_del': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'board.bigsublocality': {
            'Meta': {'object_name': 'BigSublocality'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'board.category': {
            'Meta': {'object_name': 'Category'},
            'action': ('django.db.models.fields.BooleanField', [], {}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_region': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']", 'null': 'True', 'blank': 'True'}),
            'seo_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'board.choice': {
            'Meta': {'object_name': 'Choice'},
            'advert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Advert']", 'null': 'True'}),
            'choice_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Phone']"}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Poll']"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']", 'null': 'True', 'blank': 'True'})
        },
        u'board.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'seo_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'board.cuttingwords': {
            'Meta': {'object_name': 'CuttingWords'},
            'all': ('django.db.models.fields.BooleanField', [], {}),
            'cut_words': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'condition': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'condition': ('django.db.models.fields.IntegerField', [], {'default': "(1, u'\\u0411\\u0435\\u0437 \\u0432\\u043d\\u0443\\u0442\\u0440\\u0435\\u043d\\u043d\\u0438\\u0445 \\u0440\\u0430\\u0431\\u043e\\u0442')", 'null': 'True', 'blank': 'True'}),
            'electricity': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0432 \\u0434\\u043e\\u043c\\u0435', u'\\u0432 \\u0434\\u043e\\u043c\\u0435')", 'max_length': '70', 'blank': 'True'}),
            'floors': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gaz': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0432 \\u0434\\u043e\\u043c\\u0435', u'\\u0432 \\u0434\\u043e\\u043c\\u0435')", 'max_length': '70', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lot_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lot_unit': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0441\\u043e\\u0442\\u043e\\u043a', u'\\u0441\\u043e\\u0442\\u043e\\u043a')", 'max_length': '8', 'blank': 'True'}),
            'total_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'water': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        u'board.extralot': {
            'Meta': {'object_name': 'ExtraLot'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            'electricity': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0432 \\u0434\\u043e\\u043c\\u0435', u'\\u0432 \\u0434\\u043e\\u043c\\u0435')", 'max_length': '70', 'blank': 'True'}),
            'gaz': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0432 \\u0434\\u043e\\u043c\\u0435', u'\\u0432 \\u0434\\u043e\\u043c\\u0435')", 'max_length': '70', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_purpose': ('django.db.models.fields.CharField', [], {'default': "(u'\\u0437\\u0435\\u043c\\u0435\\u043b\\u044c\\u043d\\u044b\\u0439 \\u043f\\u0430\\u0439', u'\\u0437\\u0435\\u043c\\u0435\\u043b\\u044c\\u043d\\u044b\\u0439 \\u043f\\u0430\\u0439')", 'max_length': '40', 'blank': 'True'}),
            'lot_area': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lot_unit': ('django.db.models.fields.CharField', [], {'default': "(u'\\u043a\\u0432.\\u043c\\u0435\\u0442\\u0440\\u043e\\u0432', u'\\u043a\\u0432.\\u043c\\u0435\\u0442\\u0440\\u043e\\u0432')", 'max_length': '32', 'blank': 'True'}),
            'water': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        u'board.extrarent': {
            'Meta': {'object_name': 'ExtraRent'},
            'advert': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['board.Advert']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.SmallIntegerField', [], {'default': "(2, u'\\u0414\\u043b\\u0438\\u0442\\u0435\\u043b\\u044c\\u043d\\u043e')", 'null': 'True', 'blank': 'True'})
        },
        u'board.maincategory': {
            'Meta': {'object_name': 'MainCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']", 'null': 'True', 'blank': 'True'}),
            'seo_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'board.metro': {
            'Meta': {'ordering': "['sequence_number']", 'object_name': 'Metro'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.MetroLine']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'sequence_number': ('django.db.models.fields.IntegerField', [], {})
        },
        u'board.metroline': {
            'Meta': {'object_name': 'MetroLine'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'board.objecttype': {
            'Meta': {'object_name': 'ObjectType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'board.paidadvert': {
            'Meta': {'object_name': 'PaidAdvert'},
            'advert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Advert']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']", 'null': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'board.phone': {
            'Meta': {'object_name': 'Phone'},
            'advert': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['board.Advert']", 'null': 'True', 'blank': 'True'}),
            'agent': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_addition': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']", 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'board.photo': {
            'Meta': {'ordering': "['order']", 'object_name': 'Photo'},
            'advert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Advert']"}),
            'alt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'board.poll': {
            'Meta': {'object_name': 'Poll'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 7, 28, 0, 0)'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'board.seo': {
            'Meta': {'object_name': 'Seo'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'seo_text': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'board.seogenerator': {
            'Meta': {'object_name': 'SeoGenerator'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']", 'null': 'True', 'blank': 'True'}),
            'first': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'third': ('django.db.models.fields.TextField', [], {'max_length': '4000'})
        },
        u'board.settlement': {
            'Meta': {'object_name': 'Settlement'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Sublocality']"})
        },
        u'board.street': {
            'Meta': {'ordering': "['name']", 'object_name': 'Street'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'board.sublocality': {
            'Meta': {'object_name': 'Sublocality'},
            'big_sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.BigSublocality']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_city': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'board.sublocalitydetect': {
            'Meta': {'object_name': 'SublocalityDetect'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sublocality': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Sublocality']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'personal.userdata': {
            'Meta': {'ordering': "['username']", 'object_name': 'UserData'},
            'counting_logins': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'favorite_adv': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['board.Advert']", 'symmetrical': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'memoirs': ('django.db.models.fields.TextField', [], {'max_length': '100000', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'remember': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['board']