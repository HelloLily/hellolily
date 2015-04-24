(function() {
    'use strict';

    angular.module('app.users.services', ['ngResource']);
    /**
     * Resource to get all teams that this user is part of.
     */
    angular.module('app.users.services').factory('UserTeams', UserTeams);

    UserTeams.$inject = ['$resource'];
    function UserTeams ($resource) {
        return $resource('/api/users/teams/');
    }

    /**
     * Resource to get users.
     */
    angular.module('app.users.services').factory('User', User);

    User.$inject = ['$resource'];
    function User ($resource) {
        return $resource('/api/users/user/', null, {
            me: {
                method: 'GET',
                url: '/api/users/user/me/',
                isArray: false
            },
            update: {
                method: 'PUT',
                url: '/api/users/user/:id/'
            }
        });
    }
})();

