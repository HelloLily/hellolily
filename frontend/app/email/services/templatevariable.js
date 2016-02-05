angular.module('app.email.services').factory('TemplateVariable', TemplateVariable);

TemplateVariable.$inject = ['$resource'];
function TemplateVariable($resource) {
    var _templateVariable = $resource(
        '/api/messaging/email/templatevariable/:id/',
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
