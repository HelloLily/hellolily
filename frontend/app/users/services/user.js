angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource'];
function User($resource) {
    var _user = $resource(
        '/api/users/user/:id/',
        null,
        {
            get: {
                transformResponse: function(data) {
                    var user = angular.fromJson(data);

                    user.profile_picture = decodeURIComponent(user.profile_picture);
                    return user;
                },
            },
            query: {
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
