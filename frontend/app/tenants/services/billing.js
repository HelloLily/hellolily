angular.module('app.tenants.services').factory('Billing', Billing);

Billing.$inject = ['$resource'];
function Billing($resource) {
    var _billing = $resource(
        '/api/billing/',
        {},
        {
            patch: {
                url: '/api/billing/subscription/',
                method: 'PATCH',
            },
            getBillingInfo: {
                url: '/api/billing/subscription/',
            },
            getPlans: {
                url: '/api/billing/plans/',
            },
            downloadInvoice: {
                url: '/api/billing/download_invoice/',
                method: 'POST',
            },
            getHostedPage: {
                url: '/api/billing/:action/',
                params: {
                    action: '@action',
                },
            },
            cancel: {
                url: '/api/billing/cancel/',
            },
        }
    );

    return _billing;
}
