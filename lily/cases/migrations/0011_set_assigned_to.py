# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Migrate old cases via a hardcoded dict, and new cases dynamically.
        """
        lilyuser_case_dict = {
            2: [9, 10],
            3: [88, 111, 115, 120, 137, 165, 225, 237, 248, 266, 287, 289, 290, 306, 326, 328],
            6: [145, 146, 147, 148, 172, 227, 251, 258, 261, 268],
            10: [86, 91, 133, 153, 154, 158, 160, 162, 173, 174, 178, 195, 203, 209, 218, 220, 224, 236, 246, 259, 264, 269, 271, 274, 338, 347, 350],
            11: [16],
            13: [112, 216, 231, 249, 255, 345],
            14: [87, 104, 136, 152, 156, 168, 189, 212, 213, 214, 215, 219, 221, 223, 245, 275, 305, 307, 311, 318, 352, 367],
            17: [323],
            23: [54, 57, 58, 63, 64, 65, 66, 67, 69, 70, 71, 72, 73, 92, 95, 100, 102, 106, 107, 108, 116, 117, 123, 126, 129, 138, 140, 142, 144, 149, 151, 155, 157, 167, 170, 171, 175, 179, 182, 184, 188, 191, 193, 194, 196, 198, 199, 204, 205, 210, 217, 222, 228, 229, 230, 232, 233, 234, 235, 238, 239, 243, 247, 250, 252, 260, 262, 263, 265, 267, 276, 277, 279, 281, 284, 285, 291, 295, 297, 298, 302, 319, 320, 321, 324, 330, 331, 332, 334, 335, 339, 342, 343, 346, 348, 351, 369, 370, 373],
            24: [125, 132, 141, 300, 309, 314, 317, 327, 374],
            36: [254],
            37: [6],
            38: [22, 312, 316],
            47: [74, 131, 163, 187, 190, 208, 242, 244, 270, 272, 273, 283, 288, 293, 294, 341],
            51: [17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 35, 37, 38, 39, 40, 42, 43, 44, 47, 48, 84, 103, 128, 169, 177],
            59: [49, 50, 51, 56, 61, 68, 75, 77, 78, 79, 80, 81, 82, 83, 89, 90, 101, 119, 135, 181, 183, 192, 206, 303, 304, 310, 313, 322, 329],
            60: [12, 13, 14],
            61: [150],
            63: [97, 292],
            68: [85, 93, 105, 109, 110, 113, 114, 118, 121, 122, 124, 127, 130, 164, 166, 176, 185, 197, 200, 202, 207, 211, 226, 240, 241, 253, 256, 257, 278, 280, 296, 299, 349, 358, 359],
            69: [52, 53, 55, 59, 60, 62, 94, 96, 98, 99, 134, 139, 143, 159, 161, 180, 186, 201, 282, 286, 301, 308, 315, 325, 333, 336, 337, 340, 344, 353, 354, 355, 356, 357, 360, 361, 362, 363, 364, 365, 366, 368, 371, 372]
        }

        db.start_transaction()

        # Loop through old cases to set the assigned to manually
        for lilyuser_pk, case_pk_list in lilyuser_case_dict.items():
            case_list = orm.Case.objects.filter(pk__in=case_pk_list)
            case_list.update(assigned_to2=lilyuser_pk)

        # Loop through all the new cases and set the assigned to automatically
        for case in orm.Case.objects.filter(assigned_to2_id=None):
            case.assigned_to2_id = case.assigned_to_id
            case.save()

        db.commit_transaction()

    def backwards(self, orm):
        """
        Can only be done if customuser still exists in the db.
        """
        for case in orm.Case.objects.all():
            lilyuser = case.assigned_to2
            customuser = orm['users.CustomUser'].objects.get(contact__email_addresses__email_address=lilyuser.email)
            case.assigned_to_id = customuser.pk

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
        u'cases.case': {
            'Meta': {'object_name': 'Case'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']", 'null': 'True', 'blank': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.CustomUser']"}),
            'assigned_to2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_to2'", 'null': 'True', 'to': u"orm['users.LilyUser']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 11, 17, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parcels.Parcel']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cases'", 'to': u"orm['cases.CaseStatus']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cases'", 'null': 'True', 'to': u"orm['cases.CaseType']"})
        },
        u'cases.casestatus': {
            'Meta': {'ordering': "['position']", 'unique_together': "(('tenant', 'position'),)", 'object_name': 'CaseStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        u'cases.casetype': {
            'Meta': {'object_name': 'CaseType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
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
        u'parcels.parcel': {
            'Meta': {'object_name': 'Parcel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provider': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
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
        'utils.address': {
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
        'utils.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
        },
        'utils.phonenumber': {
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



    # models = {
    #     u'accounts.account': {
    #         'Meta': {'ordering': "['name']", 'object_name': 'Account'},
    #         'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'bankaccountnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
    #         'bic': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
    #         'cocnumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
    #         'company_size': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
    #         'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
    #         'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
    #         'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'flatname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
    #         'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'legalentity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
    #         'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
    #         'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
    #         'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['socialmedia.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
    #         'taxnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
    #     },
    #     u'auth.group': {
    #         'Meta': {'object_name': 'Group'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
    #         'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
    #     },
    #     u'auth.permission': {
    #         'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
    #         'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
    #         'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
    #     },
    #     u'cases.case': {
    #         'Meta': {'object_name': 'Case'},
    #         'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']", 'null': 'True', 'blank': 'True'}),
    #         'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.LilyUser']"}),
    #         'assigned_to2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_to2'", 'null': 'True', 'to': u"orm['users.LilyUser']"}),
    #         'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']", 'null': 'True', 'blank': 'True'}),
    #         'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
    #         'expires': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 11, 17, 0, 0)'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parcels.Parcel']", 'null': 'True', 'blank': 'True'}),
    #         'priority': ('django.db.models.fields.SmallIntegerField', [], {}),
    #         'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cases'", 'to': u"orm['cases.CaseStatus']"}),
    #         'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cases'", 'null': 'True', 'to': u"orm['cases.CaseType']"})
    #     },
    #     u'cases.casestatus': {
    #         'Meta': {'ordering': "['position']", 'unique_together': "(('tenant', 'position'),)", 'object_name': 'CaseStatus'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'position': ('django.db.models.fields.IntegerField', [], {}),
    #         'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
    #     },
    #     u'cases.casetype': {
    #         'Meta': {'object_name': 'CaseType'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
    #     },
    #     u'contacts.contact': {
    #         'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Contact'},
    #         'addresses': ('lily.utils.models.fields.AddressFormSetField', [], {'to': "orm['utils.Address']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'deleted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
    #         'email_addresses': ('lily.utils.models.fields.EmailAddressFormSetField', [], {'to': "orm['utils.EmailAddress']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
    #         'gender': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
    #         'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
    #         'phone_numbers': ('lily.utils.models.fields.PhoneNumberFormSetField', [], {'to': "orm['utils.PhoneNumber']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
    #         'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
    #         'salutation': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
    #         'social_media': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['socialmedia.SocialMedia']", 'symmetrical': 'False', 'blank': 'True'}),
    #         'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
    #     },
    #     u'contenttypes.contenttype': {
    #         'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
    #         'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
    #         'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
    #     },
    #     u'parcels.parcel': {
    #         'Meta': {'object_name': 'Parcel'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
    #         'provider': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
    #     },
    #     u'socialmedia.socialmedia': {
    #         'Meta': {'object_name': 'SocialMedia'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
    #         'other_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
    #         'profile_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
    #     },
    #     u'tenant.tenant': {
    #         'Meta': {'object_name': 'Tenant'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
    #     },
    #     u'users.lilyuser': {
    #         'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'LilyUser'},
    #         'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
    #         'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
    #         'first_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
    #         'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
    #         'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '3'}),
    #         'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
    #         'last_name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
    #         'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
    #         'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
    #         'preposition': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Europe/Amsterdam'"}),
    #         'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
    #     },
    #     'utils.address': {
    #         'Meta': {'object_name': 'Address'},
    #         'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
    #         'complement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
    #         'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
    #         'state_province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
    #         'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
    #         'street_number': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
    #     },
    #     'utils.emailaddress': {
    #         'Meta': {'object_name': 'EmailAddress'},
    #         'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
    #         'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '50'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'})
    #     },
    #     'utils.phonenumber': {
    #         'Meta': {'object_name': 'PhoneNumber'},
    #         u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
    #         'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
    #         'other_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
    #         'raw_input': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
    #         'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '10'}),
    #         'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tenant.Tenant']", 'blank': 'True'}),
    #         'type': ('django.db.models.fields.CharField', [], {'default': "'work'", 'max_length': '15'})
    #     }
    # }

    complete_apps = ['users', 'cases']
    symmetrical = True
