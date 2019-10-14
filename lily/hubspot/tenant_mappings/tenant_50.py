############################################################################
# GENERAL MAPPINGS
############################################################################
from lily.contacts.models import Contact


lilyuser_to_owner_mapping = {
    3: '',  # 'sanne.bakker@voys.nl'
    4: 'joris.beltman@voys.nl',  # 'joris.beltman@voys.nl'
    6: '',  # 'werner.bergsma@voys.nl'
    10: '',  # 'giel.bouwman@voys.nl'
    13: 'steven.buurma@voys.nl',  # 'steven.buurma@voys.nl'
    14: 'miranda.smits@voys.nl',  # 'miranda.smits@voys.nl'
    23: 'johan.hilverda@voys.nl',  # 'johan.hilverda@voys.nl'
    24: 'tom.hofstede@voys.nl',  # 'tom.hofstede@voys.nl'
    33: '',  # 'anniek@voys.nl'
    35: '',  # 'ednan.pasagic@voys.nl'
    47: '',  # 'nadine.smalbil@voys.nl'
    48: '',  # 'noe@voys.nl'
    59: '',  # 'jorg.vletter@voys.nl'
    62: 'mark.vletter@voys.nl',  # 'mark.vletter@voys.nl'
    68: '',  # 'dick.wierenga@voys.nl'
    69: '',  # 'eelco.zwart@voys.nl'
    72: '',  # 'allard.stijnman@voys.nl'
    80: '',  # 'ferdy.galema@voys.nl'
    81: '',  # 'tim@voys.nl'
    82: '',  # 'dennis.huisman@voys.nl'
    84: '',  # 'steffie.hendrickx@voys.nl'
    85: 'bob.zuidema@voys.nl',  # 'bob.zuidema@voys.nl'
    86: 'annemieke.doornbos@voys.nl',  # 'annemieke.doornbos@voys.nl'
    87: 'harriet.zuidland@voys.nl',  # 'harriet.zuidland@voys.nl'
    88: '',  # 'nienke.norden@voys.nl'
    89: '',  # 'floor.koops-munneke@voys.nl'
    90: '',  # 'gijs.schuringa@voys.nl'
    93: '',  # 'bouwina@voys.nl'
    94: '',  # 'karlien@voys.nl'
    97: '',  # 'marco.vellinga@voys.nl'
    99: '',  # 'corinne.kornaat-kersten@voys.nl'
    101: '',  # 'peter.eigenraam@voys.nl'
    103: '',  # 'jellemaarten.devries@voys.nl'
    105: '',  # 'jeroen.renier@voys.nl'
    106: '',  # 'birgit.timmerman@wearespindle.com'
    108: '',  # 'redmer.loen@voys.nl'
    111: '',  # 'chantal@voys.nl'
    112: '',  # 'lisanne.boersma@voys.nl'
    116: 'ben.hoetmer@voys.nl',  # 'ben.hoetmer@voys.nl'
    119: '',  # 'william.ally@voys.nl'
    121: '',  # 'ednan@wearespindle.com'
    122: 'ritske.vanravels@voys.nl',  # 'ritske@voys.nl'
    123: 'ferdian.frericks@voys.nl',  # 'ferdian.frericks@voys.nl'
    124: 'richard.grootkarzijn@voys.nl',  # 'richard.grootkarzijn@voys.nl'
    125: '',  # 'gerjan@voys.nl'
    126: 'erik.veenstra@voys.nl',  # 'erik.veenstra@voys.nl'
    129: '',  # 'stefan@wearespindle.com'
    132: '',  # 'eva.moeyersoons@voys.be'
    133: 'gerard.verweij@voys.nl',  # 'gerard.verweij@voys.nl'
    135: '',  # 'anja.vanderwoude@voys.nl'
    137: '',  # 'tom.offringa@wearespindle.com'
    138: 'ernest.buikema@voys.nl',  # 'ernest.buikema@voys.nl'
    143: 'dennis.leenes@voys.nl',  # 'dennis.leenes@voys.nl'
    152: '',  # 'lilyapi@voys.nl'
    154: '',  # 'janneke.vandervelde@voys.nl'
    155: '',  # 'flex@voys.nl'
    156: '',  # 'cornelis.poppema+voys@wearespindle.com'
    157: 'jeroen.banus@voys.nl',  # 'jeroen.banus@voys.nl'
    158: 'arnoud.oosten@voys.nl',  # 'arnoud.oosten@voys.nl'
    159: '',  # 'mark.vanderveen@voys.nl'
    160: '',  # 'eveline.welling@voys.nl'
    162: '',  # 'sjoerd@wearespindle.com'
    168: 'marloes.vandervelde@voys.nl',  # 'marloes.vandervelde@voys.nl'
    169: 'wouter.koetze@voys.nl',  # 'wouter.koetze@voys.nl'
    226: '',  # 'arjen@hellolily.com'
    234: '',  # 'luuk@wearespindle.com'
    235: 'nina.morsa@voys.be',  # 'nina.morsa@voys.be'
    243: '',  # 'bob@wearespindle.com'
    246: '',  # 'zoe.prevoo@voys.nl'
    247: 'kirsten.beck@voys.nl',  # 'kirsten.beck@voys.nl'
    261: '',  # 'brenda.kamminga@voys.nl'
    262: 'wouter.brem@voys.nl',  # 'wouter.brem@voys.nl'
    264: '',  # 'maureen.deputter@voys.nl'
    268: '',  # 'tycho.horn@voys.nl'
    270: '',  # 'redmer+voys@wearespindle.com'
    272: '',  # 'jonathan.vandenbroek@voys.nl'
    279: '',  # 'mattijs.jager@voys.nl'
    282: '',  # 'remi+voys@wearespindle.com'
    283: '',  # 'patrick.bruinsma@voys.nl'
    284: 'irene.bottema@voys.nl',  # 'irene.bottema@voys.nl'
    324: '',  # 'bianca.koenen@voys.nl'
    472: '',  # 'janpieter@voipgrid.nl'
    478: '',  # 'lydia.dejong@voys.nl'
    534: 'sara.vanhecke@voys.be',  # 'sara.vanhecke@voys.be'
    553: '',  # 'dennis.kloetstra@voys.nl'
    637: 'yvanka.hullegie@voys.nl',  # 'yvanka.hullegie@voys.nl'
    680: 'rianne.plenter@voys.nl',  # 'rianne.plenter@voys.nl'
    734: 'pollien.vankeulen@voys.nl',  # 'pollien.vankeulen@voys.nl'
    750: 'wimke.hilvering@voys.nl',  # 'wimke.hilvering@voys.nl'
    751: 'johan.niemeijer@voys.nl',  # 'johan.niemeijer@voys.nl'
    781: 'rik.maris@voys.nl',  # 'rik.maris@voys.nl'
    847: 'niels.groenendaal@voys.nl',  # 'niels.groenendaal@voys.nl'
    850: '',  # 'marjon.paasman@voys.nl'
    865: 'peter.westerhof@voys.nl',  # 'peter.westerhof@voys.nl'
    867: '',  # 'janbart.leeuw@voys.nl'
    892: '',  # 'rik.huijzer+voys@wearespindle.com'
    904: '',  # 'renske.tans@voys.nl'
    968: 'maarten.vanbrussel@voys.nl',  # 'maarten.vanbrussel@voys.nl'
    996: '',  # 'rudolf.michaelis@voys.nl'
    997: 'maya.vanderschuit@voys.nl',  # 'maya.vanderschuit@voys.nl'
    1006: '',  # 'marco.vellinga+voys@wearespindle.com'
    1009: 'lisette.tigelaar@voys.nl',  # 'lisette.tigelaar@voys.nl'
    1064: '',  # 'pascal.visser@voys.nl'
    1094: 'nyna.vaneeks@voys.nl',  # 'nyna.vaneeks@voys.nl'
    1095: 'jetske.ouddeken@voys.nl',  # 'jetske.ouddeken@voys.nl'
    1098: '',  # 'marloes.vandekamp@voys.nl'
    1099: 'sander.bartelds@voys.nl',  # 'sander.bartelds@voys.nl'
    1105: 'anne.betting@voys.nl',  # 'anne.betting@voys.nl'
    1106: 'bart.sesselaar@voys.nl',  # 'bart.sesselaar@voys.nl'
    1107: 'nynke.kleinhorsman@voys.nl',  # 'nynke.kleinhorsman@voys.nl'
    1108: 'daniel.brouwer@voys.nl',  # 'daniel.brouwer@voys.nl'
    1112: 'jesse.mendezfonseca@voys.nl',  # 'jesse.mendezfonseca@voys.nl'
    1113: '',  # 'joest.burema+deleted@voys.nl'
    1114: 'joest.burema@voys.nl',  # 'joest.burema@voys.nl'
    1115: 'linda.hansen@voys.nl',  # 'linda.hansen@voys.nl'
    1116: '',  # 'support@voipgrid.nl'
    1117: 'leonie.vandepoll@voys.nl',  # 'leonie.vandepoll@voys.nl'
    1118: 'rick.bos@voys.nl',  # 'rick.bos@voys.nl'
}

############################################################################
# ACCOUNT MAPPINGS
############################################################################
account_status_to_company_type_mapping = {
    53: 'CUSTOMER',  # 'Active'
    54: 'OTHER',  # 'Relation'
    55: 'PROSPECT',  # 'Prospect'
    56: 'PAST_CUSTOMER',  # 'Previous customer'
    347: '',  # 'Defaulter'
    2615: 'PROSPECT',  # 'Reseller prospect'
    2616: 'RESELLER',  # 'Reseller active'
    2617: 'CUSTOMER',  # 'Active through reseller'
    2618: 'PROSPECT',  # 'Prospect through reseller'
}

############################################################################
# CONTACT MAPPINGS
############################################################################
contact_status_to_contact_status_mapping = {
    Contact.ACTIVE_STATUS: 'active',
    Contact.INACTIVE_STATUS: 'inactive',
}

############################################################################
# CASE MAPPINGS
############################################################################
case_priority_to_ticket_priority_mapping = {
    0: 'Low',
    1: 'Medium',
    2: 'High',
    3: 'High',  # Hubspot has no critical prio, so merge it with high.
}

case_pipeline = 'Support (CH) VoysNL'
case_status_to_ticket_stage_mapping = {
    50: 'New',  # 'New'
    52: 'Waiting on customer',  # 'Pending input'
    53: 'Waiting on third party',  # 'Waiting on hardware'
    54: 'Waiting on customer',  # 'Follow up'
    55: 'Waiting on customer',  # 'Client will contact us'
    56: 'Closed',  # 'Documentation'
    58: 'Closed',  # 'Closed'
}

case_type_to_ticket_category_mapping = {
    1: 'Config and send',  # 'Config and send'
    2: '',  # 'Support'
    3: 'Retour',  # 'Retour'
    4: '',  # 'Callback'
    6: 'Incident',  # 'Documentation'
    7: 'Installation',  # 'Installation'
    9: 'Callback request',  # 'Advice'
    10: 'Incident',  # 'Other'
    11: '',  # 'App'
    12: '',  # 'Cloud CTI'
    13: '',  # 'External nr unreachable'
    14: '',  # 'Freedom'
    15: '',  # 'Network related'
    16: '',  # 'One'
    17: '',  # 'Phone issue'
    18: '',  # 'PBX'
    19: '',  # 'Service interrupted'
    2343: 'Dialplan',  # 'User related'
    2344: 'Incident',  # 'Incident'
    2345: 'Administration',  # 'Administrative'
    2346: 'Administration',  # 'Bug'
    2347: 'Administration',  # 'Feature request'
}

############################################################################
# DEAL MAPPINGS
############################################################################
deal_pipeline = 'Voys NL'
deal_status_to_stage_mapping = {
    31: 'New lead - unassigned',  # 'Open'
    32: 'Proposal sent',  # 'Proposal sent'
    33: 'Done',  # 'Won'
    34: 'Lost',  # 'Lost'
    35: 'Contact',  # 'Called'
    36: 'Request feedback',  # 'Emailed'
}

deal_next_step_none_id = 4
deal_next_step_to_stage_mapping = {
    1: 'Follow up',  # 'Follow up'
    2: 'Activate',  # 'Activation'
    3: 'Request feedback',  # 'Feedback request'
    5: 'Contact',  # 'Contact'
    385: 'Proposal viewed',  # 'Viewed'
    388: 'Porting',  # 'Porting'
}

deal_found_through_to_found_through_mapping = {
    41: 'Search engine',  # 'Search engine'
    42: 'Social Media',  # 'Social media'
    43: 'Talk with employee',  # 'Talk with employee'
    44: 'Existing customer',  # 'Existing customer'
    45: 'Other',  # 'Other'
    46: 'Radio',  # 'Radio'
    47: 'Public Speaking',  # 'Public speaking'
    48: 'Press and articles',  # 'Press and articles'
    4250: 'Middleman',  # 'Middleman'
    4361: 'Call Center',  # 'Call Center'
    5429: 'Chamber of Commerce',  # 'Chamber of Commerce'
}

deal_contacted_by_to_contact_method_mapping = {
    36: 'Contact form',  # 'Quote'
    37: 'Contact form',  # 'Contact form'
    38: 'Phone',  # 'Phone'
    39: 'Web chat',  # 'Web chat'
    40: 'Email',  # 'E-mail'
    41: 'Other/ unknown',  # 'Instant connect'
    42: 'Other/ unknown',  # 'Other'
    3079: 'Other/ unknown',  # 'Cold calling'
}

deal_why_customer_to_won_reason_mapping = {
    1: 'Replaces a mobile phone number',  # 'Replaces a mobile phone number'
    2: 'Not happy at current provider',  # 'Not happy at current provider'
    3: 'Current system ready for replacement',  # 'Current system ready for replacement'
    4: 'Start of a new company',  # 'Start of a new company'
    5: 'Company is moving',  # 'Company is moving'
    6: 'Change in organisation size',  # 'Change in organisation size'
    7: 'other',  # 'Other'
    8: 'other',  # 'Unknown'
    1589: 'ISDN stops',  # 'ISDN stops'
}

deal_why_lost_to_lost_reason_mapping = {
    1: 'OTHER',  # 'Lost reason'
    2: 'Want_unlimited_calling',  # 'Wants unlimited calling'
    3: 'NO_RESPONSE_FIRST_CONTACT',  # 'No response to quote'
    4: 'Slow_response_from_Voys',  # 'Slow response from Voys'
    5: 'CANT_LEAVE_PROVIDER',  # 'Can't/won't leave current provider'
    6: 'DONT_WANT_CUSTOMER',  # 'We don't want this customer!'
    7: 'NO_RESPONSE_PROPOSAL',  # 'No response after inquiry'
    8: 'MISSING_FEATURES',  # 'Missing features'
    9: 'Voys_One_customer',  # 'Voys One customer'
    10: 'OTHER',  # 'Other'
    12: 'TOO_EXPENSIVE',  # 'Too expensive'
    13: 'No_foreign_address',  # 'No foreign address'
    3305: 'WANTS_FLATFEE',  # 'All-in-one package'
    3306: 'Only_wanted_information',  # 'Only wanted information'
    3307: 'Choose_local_provider',  # 'Chooses local provider'
    3635: 'Hardware_installation_on_site',  # 'Hardware installation on site'
    4691: 'Chooses_different_provider',  # 'Chooses different provider'
}
