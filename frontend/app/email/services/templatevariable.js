angular.module('app.email.services').factory('TemplateVariable', TemplateVariable);

TemplateVariable.$inject = ['$resource'];
function TemplateVariable($resource) {
    var _templateVariable = $resource(
        '/api/messaging/email/template-variables/:id/',
        {},
        {
            query: {
                method: 'GET',
                isArray: false,
            },
        }
    );

    return _templateVariable;
}
