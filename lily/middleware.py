

class SetRemoteAddrFromForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # On Heroku the last in the list is guaranteed to be the real one.
            real_ip = real_ip.split(",")[-1].strip()
            request.META['REMOTE_ADDR'] = real_ip
