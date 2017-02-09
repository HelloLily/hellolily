angular.module('app.email.services').factory('SharedEmailConfig', SharedEmailConfig);

SharedEmailConfig.$inject = ['$resource'];
function SharedEmailConfig($resource) {
    var _config = $resource(
        '/api/messaging/email/shared-email-configurations/',
        null,
        {
            get: {
                url: '/api/messaging/email/shared-email-configurations/?email_account=:id',
            },
            patch: {
                method: 'POST',
                params: {
                    id: '@id',
                },
            },
        });

    return _config;
}
