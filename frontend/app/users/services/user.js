angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource', 'CacheFactory'];
function User($resource, CacheFactory) {
    const cache = CacheFactory.get('userCache');
    const interceptor = {
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

            // After updating or removing a user, also invalidate user search cache.
            cache.keys().map((key) => {
                if (key.startsWith('/search/search/')) {
                    cache.remove(key);
                }
            });

            return response;
        },
    };

    const _user = $resource(
        '/api/users/:id/',
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
            unassigned: {
                method: 'GET',
                url: '/api/users/unassigned/',
                cache: CacheFactory.get('volatileCache'),
                isArray: false,
            },
            search: {
                url: '/search/search/?type=users_lilyuser&filterquery=:filterquery',
                method: 'GET',
                cache: cache,
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
            me: {
                method: 'GET',
                url: '/api/users/me/',
                isArray: false,
            },
            update: {
                method: 'PUT',
                url: '/api/users/:id/',
                interceptor: interceptor,
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
                interceptor: interceptor,
            },
            delete: {
                method: 'DELETE',
                url: '/api/users/:id/',
                interceptor: interceptor,
            },
            token: {
                method: 'GET',
                url: '/api/users/token/',
            },
            deleteToken: {
                method: 'DELETE',
                url: '/api/users/token/',
            },
            generateToken: {
                method: 'POST',
                url: '/api/users/token/',
            },
            getAssignOptions: {
                url: '/api/users/',
            },
            skipEmailAccountSetup: {
                method: 'PATCH',
                url: '/api/users/skip/',
            },
        }
    );

    return _user;
}
