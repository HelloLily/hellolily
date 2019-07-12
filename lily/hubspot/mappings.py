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
    273: 'maarten.frolich@wearespindle.com',  # original: 'maarten.frolich@wearespindle.com',
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
