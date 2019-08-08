############################################################################
# GENERAL MAPPINGS
############################################################################
from lily.contacts.models import Contact


lilyuser_to_owner_mapping = {
    15: 'luit.van.drongelen@wearespindle.com',  # original: 'luit@voipgrid.nl',
    # 17: u'tim.eebes@voipgrid.nl',
    # 18: u'joris.engbers@wearespindle.com',
    # 19: u'ferdy.galema@wearespindle.com',
    28: 'mark.leenders@wearespindle.com',  # original: 'mark.leenders@wearespindle.com',
    38: 'jan-arend.pool@voipgrid.nl',  # original: 'jan-arend.pool@voipgrid.nl',
    39: 'cornelis.poppema@wearespindle.com',  # original: 'c.poppema@gmail.com',
    # 44: u'rene.santing@wearespindle.com',
    51: 'ronald.stokebrook@voipgrid.nl',  # original: 'ronald.stokebrook@voipgrid.nl',
    # 64: u'erwin.de.vries@wearespindle.com',
    73: 'allard.stijnman@wearespindle.com',  # original: 'allard.stijnman@wearespindle.com',
    75: 'mark.vletter@wearespindle.com',  # original: 'mark@voipgrid.nl',
    # 76: u'roelinda.klip@wearespindle.com',
    91: 'jan.pieter.gorter@voipgrid.nl',  # original: 'jan.pieter.gorter@voipgrid.nl',
    # 92: u'sjoerd.romkes@wearespindle.com',
    95: 'marco.vellinga@wearespindle.com',  # original: 'marco.vellinga@wearespindle.com',
    96: 'marco.vellinga@wearespindle.com',  # original: 'marco.vellinga@voipgrid.nl',
    # 110: u'luuk.hartsema@wearespindle.com',
    # 131: u'gijs.brandsma@voipgrid.nl',
    # 134: u'arjen@wearespindle.com',
    144: 'bram.noordzij@wearespindle.com',  # original: 'bram.noordzij@wearespindle.com',
    # 161: u'eveline.welling@wearespindle.com',
    212: 'yi.ming.yung@wearespindle.com',  # original: 'yi.ming.yung@wearespindle.com',
    # 214: u'rosien.van.toor@wearespindle.com',
    # 216: u'admin@wearespindle.com',
    224: 'noe.snaterse@wearespindle.com',  # original: 'noe.snaterse@wearespindle.com',
    # 244: u'jukka.koivunen@wearespindle.com',
    273: 'maarten.frolich@voipgrid.nl',  # original: 'maarten.frolich@wearespindle.com',
    # 281: u'sjoerd+test@wearespindle.com',
    # 285: u'janneke.vandervelde@wearespindle.com',
    360: 'andreas.tieman@wearespindle.com',  # original: 'andreas.tieman@wearespindle.com',
    # 422: u'corinne.kornaat@wearespindle.com',
    # 477: u'pascal.touset@wearespindle.com',
    479: 'jasper.hafkenscheid@wearespindle.com',  # original: 'jasper.hafkenscheid@wearespindle.com',
    # 485: u'ronald.hoogma@wearespindle.com',
    # 497: u'hans.adema@wearespindle.com',
    # 519: u'ashley@wearespindle.com',
    # 529: u'joel.kuijten@wearespindle.com',
    # 552: u'antoine.beauvillain@wearespindle.com',
    # 573: u'dick.wierenga@wearespindle.com',
    # 587: u'jeremy.norman@wearespindle.com',
    # 659: u'patrick.swijgman@wearespindle.com',
    # 660: u'peter.uittenbroek@wearespindle.com',
    # 672: u'ruben.homs@wearespindle.com',
    # 674: u'henk.bokhoven@wearespindle.com',
    # 731: u'pollien.van.keulen@wearespindle.com',
    # 736: u'daniel.niemeijer@wearespindle.com',
    # 742: u'fransis.tadema@wearespindle.com',
    # 752: u'chris.kontos@wearespindle.com',
    756: 'remco.holtman@voipgrid.nl',  # original: 'remco.holtman@voipgrid.nl',
    # 787: u'jos.van.bakel@wearespindle.com',
    # 852: u'stella.tsoutsouri@wearespindle.com',
    879: 'lucas.mendes@wearespindle.com',  # original: 'lucas.mendes@wearespindle.com',
    # 905: u'ard.timmerman@wearespindle.com',
    # 920: u'janneke@voipgrid.nl',
    1005: 'dion.de.jong@wearespindle.com',  # original: 'dion.de.jong@wearespindle.com',
    # 1010: u'hylke.donker+voipgrid@wearespindle.com',
    # 1074: u'rianne.schenkel@wearespindle.com',
    1097: 'mattijs.jager@wearespindle.com',  # original: 'mattijs.jager@wearespindle.com',
}

############################################################################
# ACCOUNT MAPPINGS
############################################################################
account_status_to_company_type_mapping = {
    57: 'PARTNER',
    58: 'RELATION',
    59: 'PROSPECT',
    60: 'EX-PARTNER',
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

case_status_to_ticket_status_mapping = {
    10: 'Level 1 New',  # 'New',
    57: 'Level 1 Closed',  # 'Closed',
    70: 'Level 1 On hold',  # 'Investigating',
    71: 'Level 1 Waiting on Partner',  # 'Waiting on external party',
    72: 'Level 1 solved',  # 'Solved',
    3007: 'Level 1 Waiting on External',  # 'Waiting on supplier',
    3008: 'Level 1 Waiting on Partner',  # 'Waiting on partner',
    3009: 'Level 1 Jira ticket',  # 'Jira ticket',
}

case_type_to_ticket_category_mapping = {
    8: 'Other',  # 'Other',
    20: 'Vialer',  # 'Vialer',
    21: '',  # '_old_Activation',
    22: '',  # '_old_Bad audio',
    23: '',  # '_old_Callback',
    24: 'API',  # 'API',
    25: 'Documentation',  # 'Documentation',
    26: '',  # '_old_External_nr_unreachable',
    27: '',  # '_old_Freedom',
    28: 'Network',  # 'Network',
    29: 'Interconnect',  # 'Interconnect',
    30: 'Devices',  # 'Devices',
    31: '',  # '_old_PBX',
    32: 'Outage',  # 'Outage',
    396: 'Portal',  # 'Portal',
    2124: 'Whitelabeling',  # 'Whitelabeling',
    2125: 'Webapp',  # 'Webapp',
    2126: 'Infrastructure',  # 'Infrastructure',
    2127: '',  # 'Lily',
    2128: 'Porting',  # 'Porting',
    2129: 'Audio issues',  # 'Audio issues',
    2130: 'Financial/Billing',  # 'Financial',
    2141: 'Fraud',  # 'Fraud',
    2463: 'Number activation',  # 'Number activation',
    3012: 'Fax',  # 'Fax',
    3013: 'Portal',  # 'Portal',
    3014: 'Feature request',  # 'Feature request',
    3015: 'Wiki',  # 'Wiki',
    3016: 'Trunk',  # 'Trunk',
    3017: 'Cloudcti',  # 'Cloudcti',
    3018: 'Vialer-js',  # 'Vialer-js',
    3954: 'Provisioning',  # 'Provisioning',
}
