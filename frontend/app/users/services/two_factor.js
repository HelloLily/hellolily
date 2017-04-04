angular.module('app.users.services').factory('TwoFactor', TwoFactor);

TwoFactor.$inject = ['$resource', 'HLResource'];
function TwoFactor($resource, HLResource) {
    var _twoFactor = $resource(
        '/api/users/two-factor/',
        null,
        {
            query: {
                isArray: false,
            },
            regenerate_tokens: {
                method: 'POST',
                url: '/api/users/two-factor/regenerate_tokens/',
                isArray: true,
            },
            delete: {
                method: 'DELETE',
                url: '/api/users/two-factor/disable/',
            },
            remove_phone: {
                method: 'DELETE',
                url: '/api/users/two-factor/:id/remove_phone/',
            },
        }
    );

    /////////

    return _twoFactor;
}
