angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource', 'HLCache', 'CacheFactory'];
function User($resource, HLCache, CacheFactory) {
    var _user = $resource(
        '/api/users/user/:id/',
        null,
        {
            get: {
                cache: CacheFactory.get('dataCache'),
                transformResponse: function(data) {
                    return angular.fromJson(data);
                },
            },
            query: {
                cache: CacheFactory.get('dataCache'),
                isArray: false,
            },
            search: {
                url: '/search/search/?type=users_lilyuser&filterquery=:filterquery',
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
            me: {
                method: 'GET',
                url: '/api/users/user/me/',
                isArray: false,
            },
            update: {
                method: 'PUT',
                url: '/api/users/user/:id/',
            },
            token: {
                method: 'GET',
                url: '/api/users/user/token/',
            },
            deleteToken: {
                method: 'DELETE',
                url: '/api/users/user/token/',
            },
            generateToken: {
                method: 'POST',
                url: '/api/users/user/token/',
            },
            getAssignOptions: {
                url: '/api/users/user',
            },
        }
    );

    return _user;
}
