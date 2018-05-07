import json
import urllib
import urllib2

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from lily.utils.functions import parse_address, parse_phone_number

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView


class DataproviderView(APIView):
    """
    View that makes an API call to Dataprovider to look up information for an account.
    """
    swagger_schema = None

    def post(self, request, *args, **kwargs):
        """
        Try to retrieve account information via Dataprovider based on the url in the request.
        """
        # Construct the Dataprovider url by stripping the protocol of the query parameter.
        query_website = self._strip_protocol(request.data['url'])
        # Append the query parameters to the API url.
        dataprovider_url = self._get_dataprovider_url(query_website)

        try:
            api_output = self._do_request_to_api(dataprovider_url)
            account_information = self._get_account_information(api_output)
            return Response(account_information)
        except Exception as e:
            error = {'error': {'message': str(e)}}
            return Response(error)

    def _do_request_to_api(self, url):
        """
        Make a request to the given url and return the output.
        """
        response = urllib2.urlopen(url)
        return response.read()

    def _get_dataprovider_url(self, search_term):
        """
        Return the url to the Dataprovider API including the query string.
        """
        api_url = settings.DATAPROVIDER_API_URL
        api_key = settings.DATAPROVIDER_API_KEY

        query_params = {
            'api_key': api_key,
            'name': search_term,
        }
        return api_url + '?' + urllib.urlencode(query_params)

    def _strip_protocol(self, url):
        """
        Remove the protocol from the url.
        """
        url = url.strip()

        if url[:8] == 'https://':
                url = url[8:]
        if url[:7] == 'http://':
                url = url[7:]
        if url[:4] == 'www.':
            url = url[4:]

        return url

    def _get_account_information(self, api_output):
        """
        Create a dict with account information based on the json response from Dataprovider.
        """
        phone_number_limit = 5
        email_limit = 5
        address_limit = 3

        # Expected API output is json.
        api_output_json = json.loads(api_output)

        # Return 404 when the api returned an error.
        if api_output_json.get('error'):
            raise Http404(api_output_json.get('error'))

        # Return error message when nothing was found.
        if api_output_json.get('total') == 0:
            raise APIException(_('I\'m so sorry, I couldn\'t find any data for this website.'))

        # Filter useful data.
        result = api_output_json['data'][0]

        # Get the keywords and convert to list.
        tags = result.get('keywords')
        if tags:
            tags = result.get('keywords').strip().rstrip(',').split(',')

        # Get email addresses as a list.
        emails = list(result.get('emailaddresses', []))

        # Determine primary email since Dataprovider doesn't provide it.
        primary_email = None
        if emails:
            primary_email = self._get_primary_email(emails)

            # Set primary email to the first in the list.
            emails.index(primary_email)
            emails.remove(primary_email)
            emails.insert(0, primary_email)

        phone_numbers = []

        # Get primary phone number and convert to a nicer representation.
        phone_number = result.get('phonenumber')

        if phone_number:
            phone_number = parse_phone_number(phone_number)
            phone_numbers.append(phone_number)

        # Get phone numbers as a list.
        raw_phone_numbers = list(result.get('phonenumbers', []))

        # Convert all phone numbers to a nicer representation.
        for raw_phone_number in raw_phone_numbers:
            phone_numbers.append(parse_phone_number(raw_phone_number))

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

        # Get social media profiles.
        social_profiles = result.get('socialprofiles')

        # Group profiles by platform.
        # Disregards the other platforms provided by Dataprovider: Facebook, Google Plus and Pinterest.
        social_media = {}
        if social_profiles:
            for profile in social_profiles:
                if profile.startswith('twitter.com/'):
                    if 'twitter' not in social_media:
                        social_media['twitter'] = []
                    social_media['twitter'].append(profile)
                elif profile.startswith('www.linkedin.com/in/'):
                    if 'linkedin' not in social_media:
                        social_media['linkedin'] = []
                    social_media['linkedin'].append(profile)

        primary_twitter = ''
        if 'twitter' in social_media:
            primary_twitter = self._get_primary_profile(social_media['twitter'], result.get('company'))

        primary_linkedin = ''
        if 'linkedin' in social_media:
            primary_linkedin = self._get_primary_profile(social_media['linkedin'], result.get('company'))

        description = result.get('description')

        # Build dict with account information.
        account_information = {
            'name': result.get('company'),
            'description': description,
            'tags': tags,
            'email_addresses': emails[:email_limit],
            'primary_email': primary_email,
            'phone_numbers': phone_numbers[:phone_number_limit],
            'phone_number': phone_number,
            'addresses': addresses[:address_limit],
            'legalentity': result.get('legalentity'),
            'taxnumber': result.get('taxnumber'),
            'bankaccountnumber': result.get('bankaccountnumber'),
            'cocnumber': result.get('cocnumber'),
            'iban': result.get('iban'),
            'bic': result.get('bic'),
            'social_media_profiles': social_media,
            'twitter': primary_twitter,
            'linkedin': primary_linkedin,
        }

        return account_information

    def _get_primary_email(self, emails):
        if len(emails) > 1:
            for email in emails:
                # The main email address of a company usually starts with info@ or contact@ so check if that exists.
                if email.startswith('info') or email.startswith('contact'):
                    return email

        # Return the first email address in the list if no info@ or contact@ email could be found.
        return emails[0]

    def _get_primary_profile(self, profiles, company_name):
        """
        Determine which of the provided social media profiles is most likely the primary one.
        """
        if len(profiles) == 0:
            return ''
        if len(profiles) == 1:
            return profiles[0]

        # Maybe the social media profile has the exact company name in it.
        if company_name:
            name = company_name.lower()
            for profile in profiles:
                if profile.endswith(name):
                    return profile

        # Return the first profile if the company name couldn't be found in the profile.
        return profiles[0]
