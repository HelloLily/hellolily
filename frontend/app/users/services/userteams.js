angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams($resource) {
    const _userTeam = $resource(
        '/api/users/team/:id/',
        null,
        {
            query: {
                isArray: false,
            },
            search: {
                url: '/search/search/?type=users_team&filterquery=:filterquery',
                method: 'GET',
                transformResponse: data => {
                    const jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        total = jsonData.total;
                        objects = jsonData.hits;
                    }

                    return {
                        objects,
                        total,
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

    _userTeam.create = create;
    _userTeam.updateModel = updateModel;

    function create() {
        return new _userTeam({
            name: '',
        });
    }

    function updateModel(data, field, team) {
        const args = HLResource.createArgs(data, field, team);
        const patchPromise = HLResource.patch('UserTeams', args).$promise;

        return patchPromise;
    }

    return _userTeam;
}
