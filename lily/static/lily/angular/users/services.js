angular.module('userServices', ['ngResource'])

/**
 * Resource to get all teams that this user is part of.
 */
.factory('UserTeams', ['$resource', function($resource) {
    return $resource('/api/users/teams/')
}]);
