angular.module('app.users.services').factory('UserInvite', UserInvite);

UserInvite.$inject = ['$resource'];
function UserInvite($resource) {
    var _userInvite = $resource(
        '/api/users/invites/:id/',
        null,
        {
            post: {
                method: 'POST',
            },
            query: {
                method: 'GET',
            },
            delete: {
                method: 'DELETE',
            },
        });

    return _userInvite;
}
