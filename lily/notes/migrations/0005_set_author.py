# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ('utils', '0006_auto__add_field_historylistitem_tenant'),
    )

    def forwards(self, orm):
        """
        If this migration is done before the deletion of customuser, which it wasn't on live, then use the part at the bottom.
        Otherwise use the commented block of code
        """
        # lilyuser_note_dict = {
        #     27: [461421, 461420],
        #     68: [68343294, 68343286, 68336215, 68336213, 68298482, 68298393],
        #     69: [
        #         68343505, 68343491, 68343487, 68343259, 68342853, 68342834, 68342797, 68342718, 68342713, 68342697,
        #         68342667, 68340054, 68340053, 68339913, 68332425, 68332416, 68332317, 68329281, 68329251, 68327412,
        #         68327370, 68327227, 68327226, 68326545, 68326542, 68326409, 68326324, 68313548, 68313324, 68298949,
        #         68298853, 68298810, 68296375, 68296363, 68295927, 68277962
        #     ],
        #     38: [68341524, 68248856, 23, 13, 3],
        #     7: [21],
        #     31: [18, 6, 5, 4],
        #     37: [11],
        #     55: [1],
        #     34: [19],
        #     47: [68342559, 68341505],
        #     17: [68330967, 68330957],
        #     50: [440700, 26, 25, 24],
        #     51: [
        #         68329686, 68298589, 68295879, 68240992, 68240987, 68192360, 68189184, 68188992, 68185268, 68182266,
        #         68172874, 68144449, 68142524, 68141963, 68097774, 68097565, 68097142, 68097110, 68079960, 68079843,
        #         33744546, 24244092, 20686964, 20075251, 20074326, 17591592, 16087160, 11346994, 712004, 586032,
        #         586031, 583870, 583869, 583868, 478926, 478917
        #     ],
        #     23: [
        #         68343525, 68343524, 68343516, 68343510, 68343492, 68343332, 68343295, 68343287, 68343269, 68342494,
        #         68342437, 68342411, 68342403, 68342253, 68342143, 68341772, 68341771, 68341583, 68341530, 68341516,
        #         68341472, 68341125, 68341000, 68340975, 68340893, 68340503, 68340482, 68340407, 68340406, 68340397,
        #         68340204, 68340193, 68339884, 68339883, 68339527, 68339509, 68339400, 68339379, 68339362, 68339357,
        #         68339356, 68339320, 68339197, 68338928, 68338442, 68337973, 68337964, 68337912, 68337911, 68337878,
        #         68337846, 68337845, 68337844, 68337819, 68337806, 68337805, 68337796, 68337398, 68337384, 68337343,
        #         68337317, 68337306, 68337305, 68336640, 68336621, 68336417, 68336400, 68336220, 68336168, 68336148,
        #         68334912, 68334905, 68334890, 68334871, 68334865, 68334568, 68334317, 68334160, 68334067, 68334026,
        #         68333848, 68333813, 68333776, 68333311, 68333029, 68333021, 68332995, 68332118, 68332117, 68331899,
        #         68331708, 68331459, 68331421, 68331152, 68330971, 68330269, 68329691, 68329094, 68328906, 68328837,
        #         68328634, 68328416, 68328288, 68327770, 68327415, 68327297, 68327296, 68326710, 68326688, 68326256,
        #         68326121, 68326094, 68326091, 68325223, 68313986, 68313899, 68313642, 68313508, 68313477, 68298375,
        #         68298343, 68297969, 68297956, 68297610, 68297599, 68297571, 68297175, 68297115, 68297019, 68296943,
        #         68296907, 68296898, 68296840, 68296459, 68296345, 68296284, 68296263, 68296169, 68296157, 68296156,
        #         68239199
        #     ],
        #     59: [
        #         68342805, 68342802, 68342728, 68342558, 68342412, 68342406, 68342402, 68342386, 68341828, 68341824,
        #         68341760, 68341732, 68341603, 68341590, 68341515, 68341457, 68341112, 68340952, 68340928, 68340925,
        #         68340862, 68340396, 68340300, 68340297, 68340287, 68340272, 68340271, 68340264, 68340005, 68339882,
        #         68339461, 68339460, 68339422, 68339347, 68339295, 68339268, 68338480, 68338479, 68338478, 68338477,
        #         68338429, 68338382, 68338381, 68338371, 68338344, 68338310, 68338270, 68338237, 68338045, 68337993,
        #         68337918, 68337914, 68337516, 68337464, 68337427, 68337426, 68337411, 68337390, 68337375, 68337367,
        #         68337360, 68337350, 68337338, 68337093, 68337088, 68337087, 68337064, 68337045, 68335518, 68335517,
        #         68335369, 68335358, 68335316, 68334898, 68334897, 68334853, 68334707, 68332457, 68332448, 68332415,
        #         68332400, 68332162, 68332159, 68331929, 68331920, 68331764, 68331763, 68331471, 68331460, 68331385,
        #         68331362, 68330437, 68330378, 68330293, 68330270, 68329706, 68329690, 68328962, 68328907, 68328895,
        #         68328618, 68328512, 68328491, 68328479, 68328478, 68328264, 68326547, 68326546, 68326502, 68326388,
        #         68326360, 68326346, 68325679, 68325496, 68325283, 68325225, 68325224, 68320725, 68317722, 68314175,
        #         68314106, 68312985, 68312933, 68312626, 68312601, 68307767, 68298866, 68298791, 68298718, 68298546,
        #         68298543, 68297398, 68297357, 68297278, 68297170, 68297154, 68297100, 68297092, 68297030, 68296876,
        #         68296227, 68296171, 68296158, 68296152, 68296110, 68296109, 68296851, 68240961, 68240947, 68239669,
        #         68239649, 68239628, 68239620, 68239619, 68239561, 68239510, 68239509, 68239484, 68239286, 68239270,
        #         68239268, 68239260, 68239191, 68232398, 68220426, 68220422, 68220416, 68220411, 68220357, 68220355,
        #         68220334, 68220310, 68220303, 68220302, 68202587, 68202571
        #     ],
        #     60: [
        #         450452, 435164, 435163, 435162, 435149, 435148, 435147, 435146, 435145, 435109, 434943, 434915, 20, 17,
        #         16, 15
        #     ],
        #     61: [68199041],
        #     62: [68313579, 68298098],
        #     63: [68340891, 68338838, 68277917]
        # }
        #
        # for lilyuser_pk, note_pk_list in lilyuser_note_dict.items():
        #     note_list = orm.Note.objects.filter(pk__in=note_pk_list)
        #     note_list.update(author2=lilyuser_pk)
        #
        # # Loop through all the new cases and set the assigned to automatically
        # for note in orm.Note.objects.filter(author2_id=None):
        #     note.author2_id = note.author_id
        #     note.save()

        for note in orm.Note.objects.all():
            customuser_email = note.author.contact.email_addresses.filter(is_primary=True).first().email_address
            note.author2 = orm['users.LilyUser'].objects.get(email=customuser_email)
            note.save()

    def backwards(self, orm):
        """
        Can only be done if customuser still exists in the db.
        """
        for note in orm.Note.objects.all():
            lilyuser = note.author2
            customuser = orm['users.CustomUser'].objects.get(contact__email_addresses__email_address=lilyuser.email)
            note.author_id = customuser.pk
            note.save()

    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['name']", 'object_name': 'Account'},
            'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['socialmedia.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
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
        u'users.customuser': {
            'Meta': {'ordering': "['contact']", 'object_name': 'CustomUser', '_ormbases': [u'auth.User']},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['accounts.Account']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['contacts.Contact']"}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'contacts.contact': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Contact'},
            'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['socialmedia.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notes.note': {
            'Meta': {'ordering': "['-sort_by_date']", 'object_name': 'Note', '_ormbases': ['utils.HistoryListItem']},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.CustomUser']"}),
            'author2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'author2'", 'null': 'True', 'to': u"orm['users.LilyUser']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'historylistitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['utils.HistoryListItem']", 'unique': 'True', 'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'socialmedia.socialmedia': {
            'Meta': {'object_name': 'SocialMedia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'tenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'users.lilyuser': {
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'LilyUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '3'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Europe/Amsterdam'"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'utils.historylistitem': {
            'Meta': {'object_name': 'HistoryListItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_utils.historylistitem_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sort_by_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        u'utils.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        u'utils.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
        }
    }

    complete_apps = ['notes']
    symmetrical = True
