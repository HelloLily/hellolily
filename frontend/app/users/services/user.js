angular.module('app.users.services').factory('User', User);

User.$inject = ['$resource'];
function User($resource) {
    return $resource('/api/users/user/', null, {
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
    });
}
