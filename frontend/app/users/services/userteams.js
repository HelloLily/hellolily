angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams($resource) {
    return $resource('/api/users/team/', null, {
        mine: {
            method: 'GET',
            url: '/api/users/team/mine/',
            isArray: true,
        },
        all: {
            method: 'GET',
            url: '/api/users/team/',
            isArray: true,
        },
    });
}
