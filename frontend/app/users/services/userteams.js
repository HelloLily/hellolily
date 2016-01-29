angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams($resource) {
    var _userTeam = $resource(
        '/api/users/team/',
        null,
        {
            query: {
                isArray: false,
            },
            mine: {
                method: 'GET',
                url: '/api/users/team/mine/',
                isArray: true,
            },
        }
    );
    return _userTeam;
}
