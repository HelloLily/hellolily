angular.module('app.email.services').factory('EmailAccount', EmailAccount);

EmailAccount.$inject = ['$resource'];
function EmailAccount ($resource) {
    var EmailAccount = $resource('/api/messaging/email/account/:id/', null,
        {
            'update': { method: 'PUT' },
            'shareWith': {
                method: 'POST',
                url: '/api/messaging/email/account/:id/shared/'
            },
            'mine': {
                method: 'GET',
                url: '/api/messaging/email/account/mine/',
                isArray: true
            }
        }
    );
    return EmailAccount;
}
