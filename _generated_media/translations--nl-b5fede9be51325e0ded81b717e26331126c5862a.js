var LANGUAGE_CODE="nl";var LANGUAGE_BIDI=false;var catalog=new Array();function pluralidx(b){var a=(b!=1);if(typeof(a)=="boolean"){return a?1:0}else{return a}}catalog["%(sel)s of %(cnt)s selected"]=["",""];catalog["%(sel)s of %(cnt)s selected"][0]="%(sel)s van de %(cnt)s geselecteerd";catalog["%(sel)s of %(cnt)s selected"][1]="%(sel)s van de %(cnt)s geselecteerd";catalog["6 a.m."]="Zes uur 's ochtends";catalog["Add & edit"]="Toevoegen en bewerken";catalog.Add="Toevoegen";catalog["Available %s"]="Beschikbare %s";catalog.Calendar="Kalender";catalog.Cancel="Annuleren";catalog["Choose a time"]="Kies een tijd";catalog["Choose all"]="Kies alle";catalog.Choose="Kiezen";catalog["Chosen %s"]="Gekozen %s";catalog["Click to choose all %s at once."]="Klik om alle %s kiezen in een keer.";catalog["Click to remove all chosen %s at once."]="Klik om alle gekozen %s tegelijk te verwijderen.";catalog.Clock="Klok";catalog.Filter="Filter";catalog.Hide="Verbergen";catalog["January February March April May June July August September October November December"]="januari februari maart april mei juni juli augustus september oktober november december";catalog.Midnight="Middernacht";catalog["New account"]="Nieuw bedrijf";catalog.Noon="Twaalf uur 's middags";catalog.Now="Nu";catalog["Remove all"]="Verwijder alles";catalog.Remove="Verwijderen";catalog["S M T W T F S"]="Z M D W D V Z";catalog.Show="Tonen";catalog['This is the list of available %s. You may choose some by selecting them in the box below and then clicking the "Choose" arrow between the two boxes.']='Dit is de lijst met beschikbare %s. U kunt kiezen uit een aantal door ze te selecteren in het vak hieronder en vervolgens op de "Kiezen" pijl tussen de twee lijsten te klikken.';catalog['This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the "Remove" arrow between the two boxes.']='Dit is de lijst van de gekozen %s. Je kunt ze verwijderen door ze te selecteren in het vak hieronder en vervolgens op de "Verwijderen" pijl tussen de twee lijsten te klikken.';catalog.Today="Vandaag";catalog.Tomorrow="Morgen";catalog["Type into this box to filter down the list of available %s."]="Type in dit vak om te filteren in de lijst met beschikbare %s.";catalog.Yesterday="Gisteren";catalog["You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button."]="U heeft een actie geselecteerd en heeft geen wijzigingen gemaakt op de individuele velden. U zoekt waarschijnlijk naar de Gaan knop in plaats van de Opslaan knop.";catalog["You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action."]="U heeft een actie geselecteerd, maar heeft de wijzigingen op de individuele velden nog niet opgeslagen. Klik alstublieft op OK om op te slaan. U zult vervolgens de actie opnieuw moeten uitvoeren.";catalog["You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost."]="U heeft niet opgeslagen wijzigingen op enkele indviduele velden. Als u nu een actie uitvoert zullen uw wijzigingen verloren gaan.";function gettext(a){var b=catalog[a];if(typeof(b)=="undefined"){return a}else{return(typeof(b)=="string")?b:b[0]}}function ngettext(b,a,c){value=catalog[b];if(typeof(value)=="undefined"){return(c==1)?b:a}else{return value[pluralidx(c)]}}function gettext_noop(a){return a}function pgettext(a,b){var c=gettext(a+""+b);if(c.indexOf("")!=-1){c=b}return c}function npgettext(b,c,a,d){var e=ngettext(b+""+c,b+""+a,d);if(e.indexOf("")!=-1){e=ngettext(c,a,d)}return e}function interpolate(b,c,a){if(a){return b.replace(/%\(\w+\)s/g,function(d){return String(c[d.slice(2,-2)])})}else{return b.replace(/%s/g,function(d){return String(c.shift())})}}var formats=new Array();formats.DATETIME_FORMAT="j F Y H:i";formats.DATE_FORMAT="j F Y";formats.DECIMAL_SEPARATOR=",";formats.MONTH_DAY_FORMAT="j F";formats.NUMBER_GROUPING="3";formats.TIME_FORMAT="H:i";formats.FIRST_DAY_OF_WEEK="1";formats.TIME_INPUT_FORMATS=["%H:%M:%S","%H.%M:%S","%H.%M","%H:%M"];formats.THOUSAND_SEPARATOR=".";formats.DATE_INPUT_FORMATS=["%d-%m-%Y","%d-%m-%y","%Y-%m-%d"];formats.YEAR_MONTH_FORMAT="F Y";formats.SHORT_DATE_FORMAT="j-n-Y";formats.SHORT_DATETIME_FORMAT="j-n-Y H:i";formats.DATETIME_INPUT_FORMATS=["%d-%m-%Y %H:%M:%S","%d-%m-%y %H:%M:%S","%Y-%m-%d %H:%M:%S","%d-%m-%Y %H.%M:%S","%d-%m-%y %H.%M:%S","%d-%m-%Y %H:%M","%d-%m-%y %H:%M","%Y-%m-%d %H:%M","%d-%m-%Y %H.%M","%d-%m-%y %H.%M","%d-%m-%Y","%d-%m-%y","%Y-%m-%d"];function get_format(a){var b=formats[a];if(typeof(b)=="undefined"){return msgid}else{return b}}window.hgettext=function(a){return gettext(a)};window.hngettext=function(b,a,c){return ngettext(b,a,c)};