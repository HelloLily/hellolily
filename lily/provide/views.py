from django.http import Http404, HttpResponse
from django.views.generic.base import View
import json
import urllib
import urllib2

from lily import settings


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
        self.domain = kwargs.get('domain').strip()
        if len(self.domain) == 0:
            return Http404
        
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
    
    def get_query_string(self, **kwargs):
        if len(kwargs.keys()) > 0:
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
    api_url = 'http://alpha.dataprovider.com/api/0.1/search.php'
    api_key = settings.DATAPROVIDER_API_KEY
    
    def get_query_string(self, **kwargs):
        kwargs.update({'api_key': self.api_key,
                       'q_field': 'hostname',
                       'q_value': self.domain})
        return super(DataproviderView, self).get_query_string(**kwargs)
    
    def set_view_output(self):
        """
        Create a generic json format for account information based on the json from dataprovider.
        """
        # Expected api output is json
        self.api_output = json.loads(self.api_output)
        
        if self.api_output.get('error'):
            raise Exception(self.api_output.get('error').get('message'))
        
        result = self.api_output['results'][0]

        # Copy interesting fields to new object
        self.view_output = {
            'name': result.get('company'),
            'tags': result.get('keywords').split(','),
            'addresses': [
                {
                 'street_number': result.get('address'),
                 'street': result.get('address'),
                 'city': result.get('city'),
                 'country': result.get('country'),
                 'postal_code': result.get('zipcode'),
                },
            ],
        }
        
        return json.dumps(self.view_output)
