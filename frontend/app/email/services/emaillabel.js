angular.module('app.email.services').factory('EmailLabel', EmailLabel);

EmailLabel.$inject = ['$resource'];
function EmailLabel ($resource) {
    return $resource('/api/messaging/email/label/:id/');
}
