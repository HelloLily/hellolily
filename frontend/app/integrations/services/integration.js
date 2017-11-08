angular.module('app.integrations').factory('Integration', Integration);

Integration.$inject = ['$resource'];
function Integration($resource) {
    const _integration = $resource(
        '/api/integrations/details/:type/',
        null,
        {
            authenticate: {
                url: '/api/integrations/auth/:type/',
                method: 'POST',
                params: {
                    type: '@type',
                },
            },
            delete: {
                method: 'DELETE',
            },
        }
    );

    return _integration;
}
