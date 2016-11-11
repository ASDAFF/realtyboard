# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field favorite_adv on 'UserData'
        m2m_table_name = db.shorten_name(u'personal_userdata_favorite_adv')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userdata', models.ForeignKey(orm[u'personal.userdata'], null=False)),
            ('advert', models.ForeignKey(orm[u'board.advert'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userdata_id', 'advert_id'])

        # Adding M2M table for field groups on 'UserData'
        m2m_table_name = db.shorten_name(u'personal_userdata_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userdata', models.ForeignKey(orm[u'personal.userdata'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userdata_id', 'group_id'])

        # Adding unique constraint on 'UserData', fields ['username']
        db.create_unique(u'personal_userdata', ['username'])


        # Changing field 'UserData.current_balance'
        db.alter_column(u'personal_userdata', 'current_balance', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserData.source'
        db.alter_column(u'personal_userdata', 'source', self.gf('django.db.models.fields.CharField')(default='', max_length=20))
        # Adding field 'UserPayment.description'
        db.add_column(u'personal_userpayment', 'description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'UserPayment.order_id'
        db.add_column(u'personal_userpayment', 'order_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UserPayment.status'
        db.add_column(u'personal_userpayment', 'status',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'UserPayment.code'
        db.add_column(u'personal_userpayment', 'code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'UserPayment.transaction_id'
        db.add_column(u'personal_userpayment', 'transaction_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'UserPayment.pay_way'
        db.add_column(u'personal_userpayment', 'pay_way',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'UserPayment.sender_phone'
        db.add_column(u'personal_userpayment', 'sender_phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)


        # Changing field 'UserPayment.amount'
        db.alter_column(u'personal_userpayment', 'amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

    def backwards(self, orm):
        # Removing unique constraint on 'UserData', fields ['username']
        db.delete_unique(u'personal_userdata', ['username'])

        # Removing M2M table for field favorite_adv on 'UserData'
        db.delete_table(db.shorten_name(u'personal_userdata_favorite_adv'))

        # Removing M2M table for field groups on 'UserData'
        db.delete_table(db.shorten_name(u'personal_userdata_groups'))


        # Changing field 'UserData.current_balance'
        db.alter_column(u'personal_userdata', 'current_balance', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserData.source'
        db.alter_column(u'personal_userdata', 'source', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))
        # Deleting field 'UserPayment.description'
        db.delete_column(u'personal_userpayment', 'description')

        # Deleting field 'UserPayment.order_id'
        db.delete_column(u'personal_userpayment', 'order_id')

        # Deleting field 'UserPayment.status'
        db.delete_column(u'personal_userpayment', 'status')

        # Deleting field 'UserPayment.code'
        db.delete_column(u'personal_userpayment', 'code')

        # Deleting field 'UserPayment.transaction_id'
        db.delete_column(u'personal_userpayment', 'transaction_id')

        # Deleting field 'UserPayment.pay_way'
        db.delete_column(u'personal_userpayment', 'pay_way')

        # Deleting field 'UserPayment.sender_phone'
        db.delete_column(u'personal_userpayment', 'sender_phone')


        # Changing field 'UserPayment.amount'
        db.alter_column(u'personal_userpayment', 'amount', self.gf('django.db.models.fields.IntegerField')(default=0))

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
            'Meta': {'object_name': 'Advert'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.Category']"}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['board.City']", 'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'date_of_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        u'board.metro': {
            'Meta': {'ordering': "['name']", 'object_name': 'Metro'},
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'personal.userdata': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'UserData'},
            'counting_logins': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_balance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'favorite_adv': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['board.Advert']", 'symmetrical': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {}),
            'pay_way': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'sender_phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['personal.UserData']"})
        }
    }

    complete_apps = ['personal']