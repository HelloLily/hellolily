angular.module('app.users.services').factory('UserSession', UserSession);

UserSession.$inject = ['$resource', 'HLResource'];
function UserSession($resource, HLResource) {
    var _userSession = $resource(
        '/api/users/sessions/:session_key/',
        {session_key: '@id'},
        {
            query: {
                isArray: false,
            },
        }
    );

    /////////

    return _userSession;
}
