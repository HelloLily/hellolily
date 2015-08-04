<a name"newest-release"></a>
### Newest Release
#### Features
* 

<a name"0.4.30"></a>
### 0.4.30 (2015-07-21)
* Gulp improvements

#### Bug Fixes
* Inbox is not longer hidden if someone hides it

<a name"0.4.29"></a>
### 0.4.29 (2015-07-13)
#### Features
* Make possible to limit search in api
* improved deal form so that choices are more obvious
* e2e & frontend testing

<a name"0.4.28"></a>
### 0.4.28 (2015-07-06)
#### Features
* Make 'website' searchable in account.
* Add option to unfollow shared email addressed, both public and specifically shared

#### Bug Fixes
* Discard button doesn't sent the email anyways
* Fix for the possibility to delete emails twice
* Email address of an email account is readonly
* Searching users in the assigned to in the account form now works with spaces
* Dataprovider lookup no longer returns unparsed phone numbers

<a name"0.4.27"></a>
### 0.4.27 (2015-06-29)
#### Features

#### Bug Fixes
* Account edit/create fix so it works

<a name"0.4.26"></a>
### 0.4.26 (2015-06-26)
#### Features


#### Bug Fixes
* Restore layout of the fields on Add/Edit Account
* Fix for showing and sending emails correctly
* No more enter key to save the account form


<a name"0.4.25"></a>
### 0.4.25 (2015-06-22)

#### Features

* Changed account form to Angular
* Changing an email address to 'Primary' in account form now changes the rest to 'Other'
* Changed account API so it can deal with related fields
* Placeholders for email are simplified, `http://` is no longer required
* When replying in the historylist, if the email is flagged inactive under account/contact, it tries to find another emailaddress to reply to
* Add buttons in header are spaced (woohoo!)
* Assign case modal uses smart select searchbox
* Email addresses marked as primary will now appear at the top of the list of email addresses in various detail widgets
* Email addresses marked as inactive will no longer be displayed in detail widgets
* Search filters in listviews will no longer be cleared on hitting enter

#### Bug Fixes

* Historylist `show more` button works now with only one history type
* XSS fix in email detail view

<a name"0.4.24.1"></a>
### Hotfix 0.4.24.1 (2015-06-19)

#### Bug Fixes

* Sometimes there is no history for a message returned with Elastic search, so return empty history

## Previous Releases

<a name"0.4.24"></a>
### 0.4.24 (2015-06-18)

#### Features

* Critical cases aantal staan nu op de widgets
* Klik op email account label brengt je naar die inbox, ook als die ingeklapt is.
* Nieuwe iconen voor email account inklappen en uitklappen
* Reply & forward iconen bij mailtjes in Email & historylist
* Check of case geassigned is aan persoon of team & of case gekoppeld is aan account of contact
* cases & deals kunnen alleen verwijderd worden vanuit de detail view (niet langer in de listview)

#### Bug Fixes

Geen

<a name"0.4.23"></a>
### 0.4.23 (2015-06-11)

#### Features

* Phonenumber cleaning stript nu meer karakters
* Notes in de historylist tonen nu ook ingevoerde enters
* Inline attachments worden correct weergegeven
* Attachments gaan mee tijdens het forwarden van een mail
* Links in emails should now open outside of the iframe
* Mailboxen zijn foldable
* Bij verzenden van email wordt er gechecked of onderwerp is ingevuld & of er ontvangers zijn
* Verplichte velden zijn nu dikgedrukt

#### Bug Fixes

* Save & archive voor cases & deals werkt weer
* Verwijderde accounts worden niet meer getoond bij een contact
* Contact dat bij meerdere bedrijven werkt, toont weer alle collega's in detail view
* Een email discarden brengt je terug naar de vorige pagina (edited)
