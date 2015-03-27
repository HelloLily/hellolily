var UserServices = angular.module('UserServices', ['ngResource']);

/**
 * Resource to get all teams that this user is part of.
 */
UserServices.factory('UserTeams', ['$resource', function($resource) {
    return $resource('/api/users/teams/');
}]);

/**
 * Resource to get users.
 */
UserServices.factory('User', ['$resource', function($resource) {
    return $resource('/api/users/user/');
}]);
