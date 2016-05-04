angular.module('app.tenants.services').factory('Tenant', Tenant);

Tenant.$inject = ['$resource', '$interpolate', 'HLCache', 'CacheFactory'];
function Tenant($resource, $interpolate, HLCache, CacheFactory) {
    var _tenant = $resource(
        '/api/tenants/tenant/:id/',
        {},
        {
            query: {
                isArray: false,
                cache: CacheFactory.get('dataCache'),
                transformResponse: function(data) {
                    var tenant = angular.fromJson(data);
                    var externalAppLinkList = [];

                    if (tenant.length) {
                        tenant = tenant[0];
                    }

                    tenant.external_app_links.forEach(function(externalAppLink) {
                        externalAppLink.getUrl = function(customerId) {
                            // Substitute customer_id placeholder in the url with the actual customer id.
                            return $interpolate(externalAppLink.url)({'customer_id': customerId});
                        };

                        externalAppLinkList.push(externalAppLink);
                    });

                    if (externalAppLinkList.length) {
                        tenant.external_app_links = externalAppLinkList;
                        // Use the first link as the primary link.
                        tenant.primary_external_app_link = externalAppLinkList[0];
                    }

                    tenant.isVoysNL = function() {
                        return tenant.id === 50 || tenant.id === 2;
                    };

                    return tenant;
                },
            },
        }
    );

    return _tenant;
}
