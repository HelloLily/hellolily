#!/bin/bash

# Database.
host="localhost"
port=5433
username="hellolily"
database="hellolily"

tenants="300, 543"

queries=(
"TRUNCATE email_emailmessage CASCADE;"
"TRUNCATE email_recipient CASCADE;"  # Beacause email_emailmessage is truncated, there is no reference anymore to email_recipient.
"TRUNCATE django_session CASCADE;"
"TRUNCATE django_admin_log CASCADE"
"TRUNCATE user_sessions_session CASCADE;"
"TRUNCATE otp_static_statictoken CASCADE;"
"TRUNCATE otp_static_staticdevice CASCADE;"
"TRUNCATE otp_totp_totpdevice CASCADE;"
"TRUNCATE otp_yubikey_remoteyubikeydevice CASCADE;"
"TRUNCATE otp_yubikey_validationservice CASCADE;"
"TRUNCATE two_factor_phonedevice CASCADE;"
"TRUNCATE email_emailoutboxmessage CASCADE;"
"TRUNCATE integrations_integrationdetails CASCADE;"
"select pg_stat_reset();"
"DELETE FROM accounts_account_addresses WHERE accounts_account_addresses.account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"
"DELETE FROM accounts_account_email_addresses WHERE account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"
"DELETE FROM accounts_account_phone_numbers WHERE account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"
"DELETE FROM accounts_account_social_media WHERE account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"
"DELETE FROM accounts_website WHERE account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"  # Also removes website without a tenant.
"DELETE FROM cases_case_assigned_to_teams WHERE cases_case_assigned_to_teams.case_id IN (SELECT id FROM cases_case WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_contact_addresses WHERE contacts_contact_addresses.contact_id IN (SELECT id FROM contacts_contact WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_contact_email_addresses WHERE contacts_contact_email_addresses.contact_id IN (SELECT id FROM contacts_contact WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_contact_phone_numbers WHERE contacts_contact_phone_numbers.contact_id IN (SELECT id FROM contacts_contact WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_contact_social_media WHERE contacts_contact_social_media.contact_id IN (SELECT id FROM contacts_contact WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_function WHERE contacts_function.contact_id IN (SELECT id FROM contacts_contact WHERE tenant_id NOT IN($tenants));"
"DELETE FROM contacts_function WHERE contacts_function.account_id IN (SELECT id FROM accounts_account WHERE tenant_id NOT IN($tenants));"
"DELETE FROM deals_deal_assigned_to_teams WHERE deals_deal_assigned_to_teams.deal_id IN (SELECT id FROM deals_deal WHERE tenant_id NOT IN($tenants));"
"DELETE FROM email_gmailcredentialsmodel WHERE email_gmailcredentialsmodel.id_id IN (SELECT id FROM email_emailaccount WHERE tenant_id NOT IN($tenants));"
"DELETE FROM email_defaultemailtemplate WHERE email_defaultemailtemplate.template_id IN (SELECT id FROM email_emailtemplate WHERE tenant_id NOT IN($tenants));"
"DELETE FROM email_emaillabel WHERE email_emaillabel.account_id IN (SELECT id FROM email_emailaccount WHERE tenant_id NOT IN($tenants));"
"DELETE FROM email_emailaccount_shared_with_users WHERE email_emailaccount_shared_with_users.emailaccount_id IN (SELECT id FROM email_emailaccount WHERE tenant_id NOT IN($tenants));"
"DELETE FROM email_noemailmessageid WHERE email_noemailmessageid.account_id IN (SELECT id FROM email_emailaccount WHERE tenant_id NOT IN($tenants));"
"DELETE FROM users_lilyuser_webhooks WHERE users_lilyuser_webhooks.webhook_id IN (SELECT id FROM utils_webhook WHERE tenant_id NOT IN($tenants));"
"DELETE FROM users_lilyuser_social_media WHERE users_lilyuser_social_media.socialmedia_id IN (SELECT id FROM socialmedia_socialmedia WHERE tenant_id NOT IN($tenants));"
"DELETE FROM users_lilyuser_teams WHERE users_lilyuser_teams.team_id IN (SELECT id FROM users_team WHERE tenant_id NOT IN($tenants));"
"DELETE FROM users_lilyuser_groups WHERE users_lilyuser_groups.lilyuser_id IN (SELECT id FROM users_lilyuser WHERE tenant_id NOT IN($tenants));"
"DELETE FROM users_lilyuser_user_permissions WHERE users_lilyuser_user_permissions.lilyuser_id IN (SELECT id FROM users_lilyuser WHERE tenant_id NOT IN($tenants))"
"DELETE FROM authtoken_token WHERE authtoken_token.user_id IN (SELECT id FROM users_lilyuser WHERE tenant_id NOT IN($tenants))"
"UPDATE users_lilyuser SET primary_email_account_id = null;"  # users_lilyuser <> email_emailaccount have a circular reference, break it by setting primary email account to null.
)

tables=( "calls_calltransfer" "calls_callrecord" "calls_callparticipant" "changes_change" "email_emaildraft" "email_emaildraftattachment" "email_emailtemplateattachment" "email_sharedemailconfig" "email_templatevariable" "email_emailtemplate" "email_emailtemplatefolder" "importer_importupload" "integrations_document" "integrations_documentevent" "integrations_integrationdetails" "tags_tag" "timelogs_timelog" "users_team"  "users_userinvite" "utils_address" "utils_emailaddress" "utils_externalapplink" "utils_phonenumber" "utils_webhook" "calls_call" "notes_note" "socialmedia_socialmedia" "cases_case" "cases_casestatus" "cases_casetype" "parcels_parcel" "deals_deal" "deals_dealcontactedby" "deals_dealfoundthrough" "deals_dealnextstep" "deals_dealstatus" "deals_dealwhycustomer" "deals_dealwhylost" "email_emailaccount" "accounts_account" "accounts_accountstatus" "users_lilyuser" "contacts_contact" )

for i in "${queries[@]}"
do
	echo "$i"
	psql --username $username --host $host --port $port $database -c "$i"
	echo $'\n'
done

# Loop over all tables which have a tenant_id field and remove all data not beloning to tenant 543 and 300.
for j in "${tables[@]}"
do
	echo "DELETE FROM $j WHERE tenant_id NOT IN($tenants);"
	psql --username $username --host $host --port $port $database -c "DELETE FROM $j WHERE tenant_id NOT IN($tenants);"
	echo $'\n'
done

# Remove all tenants except 543 and 300.
echo "DELETE FROM tenant_tenant WHERE id NOT IN($tenants);"
psql --username $username --host $host --port $port $database -c "DELETE FROM tenant_tenant WHERE id NOT IN($tenants);"
echo $'\n'

echo "DELETE FROM users_userinfo WHERE users_userinfo.id NOT IN(SELECT info_id FROM users_lilyuser WHERE tenant_id IN($tenants))"
psql --username $username --host $host --port $port $database -c "DELETE FROM users_userinfo WHERE users_userinfo.id NOT IN(SELECT info_id FROM users_lilyuser WHERE tenant_id IN($tenants))"
echo $'\n'

echo "DELETE FROM billing_billing WHERE billing_billing.id NOT IN(SELECT billing_id from tenant_tenant WHERE id IN($tenants));"
psql --username $username --host $host --port $port $database -c "DELETE FROM billing_billing WHERE billing_billing.id NOT IN(SELECT billing_id from tenant_tenant WHERE id IN($tenants));"
echo $'\n'

echo "Finished in $SECONDS seconds!"

exit 1