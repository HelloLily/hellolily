var userServices = angular.module('userServices', ['ngResource']);

/**
 * Resource to get all teams that this user is part of.
 */
userServices.factory('UserTeams', ['$resource', function($resource) {
    return $resource('/api/users/teams/');
}]);
