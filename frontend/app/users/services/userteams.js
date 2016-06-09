angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams($resource) {
    var _userTeam = $resource(
        '/api/users/team/:id/',
        null,
        {
            query: {
                isArray: false,
            },
            search: {
                url: '/search/search/?type=users_lilygroup&filterquery=:filterquery',
                method: 'GET',
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
                    };
                },
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
