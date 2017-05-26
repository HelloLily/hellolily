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
                url: '/search/search/?type=users_team&filterquery=:filterquery',
                method: 'GET',
                transformResponse: function(data) {
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(function(obj) {
                                objects.push(obj);
                            });
                        }

                        total = jsonData.total;
                    }

                    return {
                        objects: objects,
                        total: total,
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
