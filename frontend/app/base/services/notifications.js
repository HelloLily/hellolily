angular.module('app.services').factory('Notifications', Notifications);

Notifications.$inject = ['$resource'];

function Notifications($resource) {
    return $resource('/api/utils/notifications/');
}
