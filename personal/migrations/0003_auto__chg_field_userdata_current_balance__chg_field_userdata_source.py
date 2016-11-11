# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserData.current_balance'
        db.alter_column(u'personal_userdata', 'current_balance', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserData.source'
        db.alter_column(u'personal_userdata', 'source', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

    def backwards(self, orm):

        # Changing field 'UserData.current_balance'
        db.alter_column(u'personal_userdata', 'current_balance', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'UserData.source'
        db.alter_column(u'personal_userdata', 'source', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

    models = {
        u'personal.userdata': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'UserData'},
            'counting_logins': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_balance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'personal.userip': {
            'Meta': {'object_name': 'UserIP'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['personal.UserData']", 'symmetrical': 'False'})
        },
        u'personal.useroperation': {
            'Meta': {'object_name': 'UserOperation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']"})
        },
        u'personal.userpayment': {
            'Meta': {'object_name': 'UserPayment'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']"})
        }
    }

    complete_apps = ['personal']