from django.http import Http404, HttpResponse
from django.views.generic.base import View
from django.utils import simplejson
import urllib
import urllib2

from lily import settings
from lily.utils.functions import parse_address


class ProvideBaseView(View):
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
            self.set_error_output(e.message)
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
        self.error_output = simplejson.dumps({'error': {'message': message}})


class DataproviderView(ProvideBaseView):
    """
    View that makes an API call to Dataprovider to look up information for accounts.
    """
    api_url = 'http://www.dataprovider.com/api/0.1/search.php'
    api_key = settings.DATAPROVIDER_API_KEY

    def get_domain(self):
        """
        Return domain without http:// but with 'www.'
        """
        self.domain = super(DataproviderView, self).get_domain()

        if self.domain[:6] == 'http://':
                self.domain = self.domain[6:]
        if self.domain[:4] == 'www.':
            self.domain = self.domain[4:]

        return self.domain

    def get_query_kwargs(self):
        kwargs = {'api_key': self.api_key,
                       'q_field': 'hostname',
                       'q_value': self.domain,
#                       'q_operator': 5 # filter: ends with
        }
        return kwargs

    def set_view_output(self, retry=False):
        """
        Create a generic json format for account information based on the json from dataprovider.
        """
        # Expected api output is json
        self.api_output = simplejson.loads(self.api_output)

        # Return 404 when nothing was found
        if self.api_output.get('found') == 0:
            if not retry:
                # No luck without leading www., try with www.:
                self.domain = 'www.' + self.domain
                # Retry
                self.api_output = self.do_request_to_api(self.get_url())
                self.set_view_output(retry=True)
            else:
                raise Http404()

        # Raise exception when the api returned an error
        if self.api_output.get('error'):
            raise Exception(self.api_output.get('error').get('message'))

        # Filter useful data
        result = self.api_output['results'][0]


        company = result.get('company').replace('\\', '') if result.get('company') else None
        description = result.get('description').replace('\\', '') if result.get('description') else None
        tags = result.get('keywords').strip().rstrip(',').split(',') if result.get('keywords') else []
        email_addresses = [result.get('emails')] if result.get('emails') else []
        phone_numbers = [result.get('phonenumber')] if result.get('phonenumber') else []
        legalentity = result.get('legalentity') if result.get('legalentity') else None
        taxnumber = result.get('taxnumber') if result.get('taxnumber') else None
        bankaccountnumber = result.get('bankaccountnumber') if result.get('bankaccountnumber') else None
        cocnumber = result.get('cocnumber') if result.get('cocnumber') else None
        iban = result.get('iban') if result.get('iban') else None
        bic = result.get('bic') if result.get('bic') else None

        address = result.get('address') if result.get('address') else None
        if address:
            street, street_number, complement = parse_address(address)
        else:
            street, street_number, complement = None, None, None

        addresses = [{
            'street': street,
            'street_number': street_number,
            'complement': complement,
            'city': result.get('city'),
            'country': result.get('country'),
            'postal_code': result.get('zipcode'),
        }] if address or result.get('city') or result.get('zipcode') or result.get('country') else []

        # Build dict with account information
        self.view_output = {
            'name': company,
            'description': description,
            'tags': tags,
            'email_addresses': email_addresses,
            'phone_numbers': phone_numbers,
            'addresses': addresses,
            'legalentity': legalentity,
            'taxnumber': taxnumber,
            'bankaccountnumber': bankaccountnumber,
            'cocnumber': cocnumber,
            'iban': iban,
            'bic': bic,
        }

        return simplejson.dumps(self.view_output)

    def get_view_output(self):
        return HttpResponse(self.view_output, mimetype='application/json')

    def get_error_output(self):
        raise Http404()
