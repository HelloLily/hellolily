<a name"next-release"></a>
## Next Release

<a name"0.4.25"></a>
### 0.4.25 ()

#### Features

* Changed account form to Angular
* Changing an email address to 'Primary' in account form now changes the rest to 'Other'
* Changed account API so it can deal with related fields
* Placeholders for email are simplified, `http://` is no longer required
* When replying in the historylist, if the email is flagged inactive under account/contact, it tries to find another emailaddress to reply to
* 

#### Bug Fixes

* Historylist `show more` button works now with only one history type
*

<a name"latest-release"></a>
## Latest Release

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
