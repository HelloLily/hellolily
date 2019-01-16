angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource', 'CacheFactory'];
function UserTeams($resource, CacheFactory) {
    const _userTeam = $resource(
        '/api/users/team/:id/',
        null,
        {
            query: {
                isArray: false,
                cache: CacheFactory.get('volatileCache'),
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
                cache: CacheFactory.get('volatileCache'),
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
