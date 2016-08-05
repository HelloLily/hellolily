angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource', 'CacheFactory'];
function User($resource, CacheFactory) {
    var cache = CacheFactory.get('userCache');
    var interceptor = {
        // Interceptor used to remove/update the cache on update/delete.
        response: function(response) {
            var cacheKey = response.config.url;

            if (response.config.params) {
                cacheKey += '?' + response.config.paramSerializer(response.config.params);
            }

            if (response.data) {
                // New data was returned, so use that for the cache.
                cache.put(cacheKey, response.data);
            } else {
                // No new data was returned, so delete the cache.
                cache.remove(cacheKey);
            }

            return response;
        },
    };

    var _user = $resource(
        '/api/users/user/:id/',
        null,
        {
            get: {
                cache: cache,
                transformResponse: function(data) {
                    return angular.fromJson(data);
                },
            },
            query: {
                cache: cache,
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
                interceptor: interceptor,
            },
            patch: {
                method: 'PATCH',
                url: '/api/users/user/:id/',
                interceptor: interceptor,
            },
            delete: {
                method: 'DELETE',
                url: '/api/users/user/:id/',
                interceptor: interceptor,
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
