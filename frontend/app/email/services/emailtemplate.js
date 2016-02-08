angular.module('app.email.services').factory('EmailTemplate', EmailTemplate);

EmailTemplate.$inject = ['$resource'];
function EmailTemplate($resource) {
    var _emailTemplate = $resource(
        '/api/messaging/email/emailtemplate/:id/',
        {},
        {
            query: {
                isArray: false,
            },
        }
    );
    return _emailTemplate;
}
