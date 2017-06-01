angular.module('app.tenants.services').factory('Tenant', Tenant);

Tenant.$inject = ['$filter', '$interpolate', '$resource', 'CacheFactory', 'HLCache'];
function Tenant($filter, $interpolate, $resource, CacheFactory, HLCache) {
    var _tenant = $resource(
        '/api/tenants/:id/',
        {},
        {
            getAccountAdmin: {
                url: '/api/tenants/admin/',
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            query: {
                isArray: false,
                cache: CacheFactory.get('dataCache'),
                transformResponse: data => {
                    var tenant = angular.fromJson(data);
                    var externalAppLinkList = [];

                    if (tenant.length) {
                        tenant = tenant[0];
                    }

                    tenant.external_app_links.forEach(externalAppLink => {
                        externalAppLink.getUrl = customerId => {
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

                    tenant.isVoysNL = () => {
                        return tenant.id === 50 || debug;
                    };

                    tenant.isVoysSA = () => {
                        return tenant.id === 52;
                    };

                    // Check if PandaDoc integration is set for the tenant.
                    tenant.hasPandaDoc = $filter('contains')(tenant.integrations, 'type === 1');

                    // Check if Moneybird integration is set for the tenant.
                    tenant.hasMoneybird = $filter('contains')(tenant.integrations, 'type === 2');

                    return tenant;
                },
            },
        }
    );

    return _tenant;
}
