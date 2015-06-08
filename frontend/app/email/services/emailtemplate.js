angular.module('app.email.services').factory('EmailTemplate', EmailTemplate);

EmailTemplate.$inject = ['$resource'];
function EmailTemplate ($resource) {
    return $resource('/api/messaging/email/emailtemplate/:id/');
}
