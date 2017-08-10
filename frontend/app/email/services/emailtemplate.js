angular.module('app.email.services').factory('EmailTemplate', EmailTemplate);

EmailTemplate.$inject = ['$resource'];
function EmailTemplate($resource) {
    var _emailTemplate = $resource(
        '/api/messaging/email/templates/:id/',
        {},
        {
            query: {
                isArray: false,
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            move: {
                method: 'PATCH',
                url: '/api/messaging/email/templates/move/',
            },
        }
    );

    return _emailTemplate;
}
