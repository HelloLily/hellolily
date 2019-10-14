############################################################################
# GENERAL MAPPINGS
############################################################################
from lily.contacts.models import Contact


lilyuser_to_owner_mapping = {
    259: 'info@voys.co.za',  # admin@voys.co.za
    740: 'guillaume@voys.co.za',  # guillaume@voys.co.za
    242: 'info@voys.co.za',  # klantgeluk@voys.nl
    232: '',  # sjoerd+@wearespindle.com
    1102: 'uda@voys.co.za',  # kuda@voys.co.za
    258: 'mark.vletter@voys.nl',  # mark@voys.nl
    71: 'athini@voys.co.za',  # athini@voys.co.za
    510: 'sakhe@voys.co.za',  # sakhe@voys.co.za
    70: 'sebastiaan@voys.co.za',  # sebastiaan@voys.co.za
    1096: 'yoann@voys.co.za',  # yoann@voys.co.za
    667: 'thea@voys.co.za',  # thea@voys.co.za
    763: 'reagan@voys.co.za',  # reagan@voys.co.za
    297: 'roxzanne@voys.co.za',  # roxzanne@voys.co.za
    295: 'natalie@voys.co.za',  # natalie@voys.co.za
    930: 'loyiso@voys.co.za',  # loyiso@voys.co.za
}

############################################################################
# ACCOUNT MAPPINGS
############################################################################
account_status_to_company_type_mapping = {
    61: 'CUSTOMER',  # Active
    62: 'OTHER',  # Relation
    63: 'PROSPECT',  # Prospect
    64: 'PAST_CUSTOMER',  # Previous customer
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

case_pipeline = 'Support Voys SA'
case_status_to_ticket_stage_mapping = {
    59: 'New',  # New
    60: 'Waiting on us',  # Problem definition
    61: 'Waiting on us',  # Troubleshooting
    62: 'Waiting on customer',  # Waiting for customer
    63: 'Waiting on third party',  # Waiting for upstream provider
    64: 'Closed',  # Resolved
}

case_type_to_ticket_category_mapping = {
    33: 'Callback request',  # Advice
    34: 'Voys App',  # App
    35: 'Callback request',  # Callback
    36: 'Dialplan',  # Cloud CTI
    37: 'Config and Send',  # Config and send
    38: 'Administration',  # Documentation
    39: 'Incident',  # External nr unreachable
    40: 'Dialplan',  # Freedom
    41: 'Installation',  # Installation
    42: 'Incident',  # Network related
    43: 'Incident',  # One
    44: 'Incident',  # Other
    45: 'Devices',  # PBX
    46: 'Devices',  # Phone issue
    47: 'Retour',  # Retour
    48: 'Incident',  # Service interrupted
    54: 'Incident',  # Support
}

############################################################################
# DEAL MAPPINGS
############################################################################
deal_pipeline = 'Voys SA'
deal_status_to_stage_mapping = {
    37: 'Proposal sent',  # Open
    39: 'Won',  # Won
    40: 'Lost',  # Lost
    41: 'New lead - unassigned',  # New
    287: 'Proposal signed - Waiting for documents',  # Documents
}

deal_next_step_none_id = 24
deal_next_step_to_stage_mapping = {
    342: 'First contact',  # First contact
    343: 'Proposal sent',  # Follow-up
    344: 'Activate',  # Activate service
    345: 'Activate',  # Ship hardware
    346: 'Porting',  # Porting documents received?
    347: 'Won',  # Request feedback
    348: 'Proposal sent',  # First follow-up
    349: 'Send proposal',  # Send proposal
    386: 'Porting',  # Port approval received?
    387: 'Porting',  # Port activation
    402: 'Won',  # Courtesy call
    2489: 'Proposal signed - Waiting for documents',  # Request documents
}

deal_found_through_to_found_through_mapping = {
    49: 'Search engine',  # Search engine
    50: 'Social Media',  # Social media
    51: 'Talk with employee',  # Talk with employee
    52: 'Referral',  # Referral
    53: 'Other',  # Other
    54: 'Radio',  # Radio
    55: 'Public speaking',  # Public speaking
    56: 'Press and articles',  # Press and articles
}

deal_contacted_by_to_contact_method_mapping = {
    44: 'Contact form',  # Contact form
    45: 'Phone',  # Phone
    46: 'Web chat',  # Web chat
    47: 'Email',  # E-mail
    49: 'Other/ unknown',  # Other
}

deal_why_customer_to_won_reason_mapping = {
    9: 'Replaces a mobile phone number',  # Replacing mobile phone number
    10: 'Not happy at current provider',  # Not happy with current provider
    11: 'Current system ready for replacement',  # Current system due for replacement
    12: 'Start of a new company',  # Starting a new company
    13: 'Company is moving',  # Company is moving
    14: 'Change in organisation size',  # Change in organization size
    15: 'Other',  # Other
    16: 'Other',  # Unknown
}

deal_why_lost_to_lost_reason_mapping = {
    507: 'NO_RESPONSE_FIRST_CONTACT',  # Does not respond to first contact
    508: 'NO_RESPONSE_PROPOSAL',  # Does not respond after proposal
    509: 'OTHER',  # Slow response from Voys
    510: 'CANT_LEAVE_PROVIDER',  # Can't/won't leave current provider
    511: 'DONT_WANT_CUSTOMER',  # We don't want this customer!
    512: 'MISSING_FEATURES',  # Missing features
    513: 'TOO_EXPENSIVE',  # Too expensive
    514: 'WANTS_VOICE_DATA',  # Wants voice and data package
    515: 'INSUFFICIENT_CONNECTIVITY',  # Connectivity not sufficient
    516: 'RENT_HARDWARE',  # Wants to rent hardware
    517: 'OTHER',  # Other
    518: 'PRIVATE_USE',  # For private use
}
