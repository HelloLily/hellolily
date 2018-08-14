from datetime import timedelta, date


def create_defaults_for_tenant(tenant):
    # Do imports locally to prevent circular imports.
    from lily.accounts.models import Account, Website, AccountStatus
    from lily.cases.models import Case, CaseType, CaseStatus
    from lily.contacts.models import Contact, Function
    from lily.deals.models import (
        DealContactedBy, DealFoundThrough, DealNextStep, DealWhyCustomer, DealWhyLost, DealStatus
    )
    from lily.messaging.email.models.models import EmailTemplate
    from lily.socialmedia.models import SocialMedia
    from lily.users.models import Team, LilyUser
    from lily.utils.models.models import EmailAddress

    # Team
    team_list = [
        'Sales',
        'Customer care',
        'Finance',
    ]
    Team.objects.bulk_create([Team(tenant=tenant, name=name) for name in team_list])

    # AccountStatus
    account_status_list = [
        'Customer',
        'Relation',
        'Prospect',
        'Former customer',
    ]
    AccountStatus.objects.bulk_create([
        AccountStatus(tenant=tenant, position=position, name=name)
        for position, name in enumerate(account_status_list, start=1)
    ])

    # CaseType
    case_type_list = [
        'Callback',
        'Support',
        'Finance',
        'Sales',
        'Other',
    ]
    CaseType.objects.bulk_create([CaseType(tenant=tenant, name=name) for name in case_type_list])

    # CaseStatus
    case_status_list = [
        'New',
        'Processing',
        'Pending input',
        'Follow up',
        'Closed',
    ]
    CaseStatus.objects.bulk_create([
        CaseStatus(tenant=tenant, position=position, name=name)
        for position, name in enumerate(case_status_list, start=1)
    ])

    # DealContactedBy
    deal_contact_by_list = [
        'Phone',
        'Website form',
        'Email',
        'Chat',
        'Social media',
        'Exhibition',
        'Other',
    ]
    DealContactedBy.objects.bulk_create([
        DealContactedBy(tenant=tenant, position=position, name=name)
        for position, name in enumerate(deal_contact_by_list, start=1)
    ])

    # DealFoundThrough
    deal_found_through_list = [
        'Search engine',
        'Social media',
        'Talk with employee',
        'Existing customer',
        'Cold calling',
        'Public speaking',
        'Press and articles',
        'Exhibition',
        'Radio/TV',
        'Other',
    ]
    DealFoundThrough.objects.bulk_create([
        DealFoundThrough(tenant=tenant, position=position, name=name)
        for position, name in enumerate(deal_found_through_list, start=1)
    ])

    # DealNextStep
    deal_next_steps = (
        ('Contact', '1'),
        ('Follow up', '5'),
        ('Waiting on client', '10'),
        ('Aftersales', '20'),
        ('None', '0'),
    )
    DealNextStep.objects.bulk_create([
        DealNextStep(tenant=tenant, position=position, name=next_step[0], date_increment=next_step[1])
        for position, next_step in enumerate(deal_next_steps, start=1)
    ])

    # DealWhyCustomer
    deal_why_customer_list = [
        'Not happy with current supplier',
        'Start of new business',
        'Expansion of current business',
        'Interested in our product(s)',
        'Other',
    ]
    DealWhyCustomer.objects.bulk_create([
        DealWhyCustomer(tenant=tenant, position=position, name=name)
        for position, name in enumerate(deal_why_customer_list, start=1)
    ])

    # DealWhyLost
    deal_why_lost_list = [
        'Too expensive',
        'No response after inquiry',
        'No response to quote',
        'We replied too late',
        'Not a customer for us',
        'Missing features',
        'Other',
    ]
    DealWhyLost.objects.bulk_create([
        DealWhyLost(tenant=tenant, position=position, name=name)
        for position, name in enumerate(deal_why_lost_list, start=1)
    ])

    # DealStatus
    deal_status_list = [
        'New',
        'Open',
        'Won',
        'Lost',
    ]
    DealStatus.objects.bulk_create([
        DealStatus(tenant=tenant, position=position, name=name)
        for position, name in enumerate(deal_status_list, start=1)
    ])

    # Team Lily
    email_address = EmailAddress.objects.create(
        email_address='support@hellolily.com',
        status=EmailAddress.PRIMARY_STATUS,
        tenant=tenant,
    )

    account_status = AccountStatus.objects.get(name='Relation', tenant=tenant)

    account = Account.objects.create(
        tenant=tenant,
        name='Team Lily',
        description=(
            'Team Lily has been added automatically. Feel free to add all the other companies,'
            'organizations and other parties you get in touch with as Accounts.'
        ),
        status=account_status,
    )

    website = Website.objects.create(
        website='https://hellolily.com',
        is_primary=True,
        account=account,
        tenant=tenant,
    )

    twitter = SocialMedia.objects.create(
        tenant=tenant,
        name='twitter',
        username='sayhellolily',
        profile_url='https://twitter.com/sayhellolily',
    )

    account.email_addresses.add(email_address)
    account.websites.add(website)
    account.social_media.add(twitter)

    # Add Team Lily default contacts
    lily_contacts = [{
        'first_name': 'Sjoerd',
        'last_name': 'Romkes',
        'email_address': 'sjoerd@hellolily.com',
    }, {
        'first_name': 'Support',
        'last_name': 'Lily',
        'email_address': 'lily@hellolily.com',
    }]

    for contact in lily_contacts:
        contact_instance = Contact.objects.create(
            tenant=tenant,
            gender=0,
            first_name=contact['first_name'],
            last_name=contact['last_name'],
        )

        contact_email = EmailAddress.objects.create(
            email_address=contact['email_address'],
            status=EmailAddress.PRIMARY_STATUS,
            tenant=tenant,
        )
        Function.objects.create(account=account, contact=contact_instance)
        contact_instance.email_addresses.add(contact_email)

    description = (
        'A case can be used for tasks which take more than a couple of minutes to complete.'
        '\nFor example extensive customer service or technical questions.'
        '\n\nTo solve this case, send an email to Team Lily with your first thoughts, concerns or questions.'
        '\nAfterwards, close this case by clicking \'Closed\' since you\'ve solved it.'
        '\nThat\'s it, you\'ve completed your first case!'
    )

    Case.objects.create(
        account=account,
        contact=Contact.objects.filter(tenant=tenant).first(),
        subject='Team Lily needs your input!',
        description=description,
        status=CaseStatus.objects.get(name='New', tenant=tenant),
        type=CaseType.objects.get(name='Support', tenant=tenant),
        priority=Case.LOW_PRIO,
        expires=date.today() + timedelta(days=7),
        assigned_to=LilyUser.objects.filter(tenant=tenant).first(),
        tenant=tenant,
    )

    EmailTemplate.objects.create(
        name='Example signature',
        subject='',
        body_html=(
            'Regards,<br>'
            '[[ user.full_name ]]<br>'
            'Phone: [[ user.phone_number ]]<br>'
            'Email: [[ user.current_email_address ]]'
        ),
        tenant=tenant,
    )
