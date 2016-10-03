angular.module('app.email.services').factory('EmailAccount', EmailAccount);

EmailAccount.$inject = ['$resource'];
function EmailAccount($resource) {
    var _emailAccount = $resource(
        '/api/messaging/email/accounts/:id/',
        null,
        {
            query: {
                isArray: false,
            },
            'update': {
                method: 'PUT',
            },
            'shareWith': {
                method: 'POST',
                url: '/api/messaging/email/accounts/:id/shared/',
            },
            'mine': {
                method: 'GET',
                url: '/api/messaging/email/accounts/mine/',
                isArray: true,
            },
        }
    );
    return _emailAccount;
}
