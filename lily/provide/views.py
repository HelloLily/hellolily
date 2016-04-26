import json
import urllib
import urllib2

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View

from lily.utils.functions import parse_address, parse_phone_number
from lily.utils.views import LoginRequiredMixin


class ProvideBaseView(LoginRequiredMixin, View):
    """
    Base view for external APIs which can provide data.
    """
    http_method_names = ['get']
    domain = None
    api_url = None
    api_output = None
    view_output = None
    error_output = None

    def get(self, request, *args, **kwargs):
        """
        Save domain from Request or return 404 if the domain is empty.
        """
        # get domain
        self.kwargs = kwargs
        self.domain = self.get_domain()

        self.api_output = self.do_request_to_api(self.get_url())

        try:
            self.view_output = self.set_view_output()
            return self.get_view_output()
        except Exception as e:
            self.set_error_output(str(e))
            return self.get_error_output()

    def get_url(self):
        return self.get_api_url() + self.get_query_string()

    def get_api_url(self):
        return self.api_url

    def get_domain(self):
        return self.domain or self.kwargs.get('domain').strip()

    def get_query_kwargs(self):
        return {}

    def get_query_string(self):
        kwargs = self.get_query_kwargs()
        if len(kwargs) > 0:
            return '?' + urllib.urlencode(kwargs)
        return ''

    def do_request_to_api(self, url):
        """
        Make a request to the given url and return the output.
        """
        response = urllib2.urlopen(url)
        return response.read()

    def get_view_output(self):
        return HttpResponse(self.view_output)

    def set_view_output(self):
        raise NotImplementedError

    def get_error_output(self):
        return HttpResponse(self.error_output)

    def set_error_output(self, message):
        self.error_output = json.dumps({'error': {'message': message}})


class DataproviderView(ProvideBaseView):
    """
    View that makes an API call to Dataprovider to look up information for accounts.
    """
    api_url = 'https://www.dataprovider.com/api/0.1/lookup/hostname.json'
    api_key = settings.DATAPROVIDER_API_KEY

    def get_domain(self):
        """
        Return domain without http:// but with 'www.'
        """
        self.domain = super(DataproviderView, self).get_domain()

        if self.domain[:8] == 'https://':
                self.domain = self.domain[8:]
        if self.domain[:7] == 'http://':
                self.domain = self.domain[7:]
        if self.domain[:4] == 'www.':
            self.domain = self.domain[4:]

        return self.domain

    def get_query_kwargs(self):
        kwargs = {
            'api_key': self.api_key,
            'name': self.domain,
        }
        return kwargs

    def set_view_output(self):
        """
        Create a generic json format for account information based on the json from Dataprovider.
        """
        phone_number_limit = 5
        email_limit = 5
        address_limit = 3

        # Expected api output is json.
        self.api_output = json.loads(self.api_output)

        # Return 404 when the api returned an error.
        if self.api_output.get('error'):
            raise Http404()

        # Return error message when nothing was found.
        if self.api_output.get('total') == 0:
            raise Exception(_('I\'m so sorry, I couldn\'t find any data for this website.'))

        # Filter useful data.
        result = self.api_output['data'][0]

        # Get company name.
        company = result.get('company')

        # Get website description.
        description = result.get('description')

        # Get the keywords and convert to list.
        tags = result.get('keywords')
        if tags:
            tags = result.get('keywords').strip().rstrip(',').split(',')

        # Get email addresses and convert to a list if needed.
        emails = result.get('emailaddresses', []) or []
        if not isinstance(emails, list):
            emails = [emails]

        # Determine primary email since Dataprovider doesn't provide it.
        primary_email = None
        if emails:
            primary_email = self._get_primary_email(emails)

            # Set primary email to the first in the list.
            emails.index(primary_email)
            emails.remove(primary_email)
            emails.insert(0, primary_email)

        # Limit number of emails.
        emails = emails[:email_limit]

        phone_numbers = []

        # Get primary phone number and convert to a nicer representation.
        phone_number = result.get('phonenumber')

        if phone_number:
            phone_number = parse_phone_number(phone_number)
            phone_numbers.append(phone_number)

        # Get phone numbers and convert to list if needed.
        raw_phone_numbers = result.get('phonenumbers', []) or []
        if not isinstance(raw_phone_numbers, list):
            raw_phone_numbers = [raw_phone_numbers]

        # Convert all phone numbers to a nicer representation.
        for raw_phone_number in raw_phone_numbers:
            phone_numbers.append(parse_phone_number(raw_phone_number))

        # Limit number of phonenumbers.
        phone_numbers = phone_numbers[:phone_number_limit]

        # Get what kind of company it is (e.g. LLC).
        legalentity = result.get('legalentity')

        # Get the VAT (Value Added Tax) identifaction number.
        taxnumber = result.get('taxnumber')

        # Get bank account number.
        bankaccountnumber = result.get('bankaccountnumber')

        # Get the CoC (Chamber of Commerce) number.
        cocnumber = result.get('cocnumber')

        # Get the IBAN (Internation Bank Account Number).
        iban = result.get('iban')

        # Get the BIC (Bank Identifier Code).
        bic = result.get('bic')

        # Try to parse the address.
        address = result.get('address')
        address_line = ''
        if address:
            # Construct address_line, instead of assigning address to address_line directly,
            # because parse_address() also santizes the result.
            street, street_number, complement = parse_address(address)
            if street:
                address_line = street
            if street_number:
                address_line += ' ' + street_number
            if complement:
                address_line += complement

        # Make the full address.
        addresses = []
        if address or result.get('city') or result.get('zipcode') or result.get('country'):
            addresses = [{
                'address': address_line,
                'city': result.get('city'),
                'country': result.get('country'),
                'postal_code': result.get('zipcode'),
            }]

        addresses = addresses[:address_limit]

        # Build dict with account information.
        self.view_output = {
            'name': company,
            'description': description,
            'tags': tags,
            'email_addresses': emails,
            'primary_email': primary_email,
            'phone_numbers': phone_numbers,
            'phone_number': phone_number,
            'addresses': addresses,
            'legalentity': legalentity,
            'taxnumber': taxnumber,
            'bankaccountnumber': bankaccountnumber,
            'cocnumber': cocnumber,
            'iban': iban,
            'bic': bic,
        }

        return json.dumps(self.view_output)

    def get_view_output(self):
        return HttpResponse(self.view_output, content_type='application/json')

    def _get_primary_email(self, emails):
        if len(emails) > 1:
            for email in emails:
                # The main email address of a company usually starts with info@ or contact@ so check if that exists.
                if email.startswith('info') or email.startswith('contact'):
                    return email

        # Return the first email address in the list if no info@ or contact@ email could be found.
        return emails[0]
