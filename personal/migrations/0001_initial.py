# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserData'
        db.create_table(u'personal_userdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('counting_logins', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('current_balance', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'personal', ['UserData'])

        # Adding model 'UserPayment'
        db.create_table(u'personal_userpayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.UserData'])),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('annotation', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'personal', ['UserPayment'])

        # Adding model 'UserIP'
        db.create_table(u'personal_userip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.UserData'])),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'personal', ['UserIP'])

        # Adding model 'UserOperation'
        db.create_table(u'personal_useroperation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personal.UserData'])),
            ('operation', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'personal', ['UserOperation'])


    def backwards(self, orm):
        # Deleting model 'UserData'
        db.delete_table(u'personal_userdata')

        # Deleting model 'UserPayment'
        db.delete_table(u'personal_userpayment')

        # Deleting model 'UserIP'
        db.delete_table(u'personal_userip')

        # Deleting model 'UserOperation'
        db.delete_table(u'personal_useroperation')


    models = {
        u'personal.userdata': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'UserData'},
            'counting_logins': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_balance': ('django.db.models.fields.IntegerField', [], {}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'personal.userip': {
            'Meta': {'object_name': 'UserIP'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']"})
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