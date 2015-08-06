angular.module('app.email.services').factory('TemplateVariable', TemplateVariable);

TemplateVariable.$inject = ['$resource'];
function TemplateVariable($resource) {
    return $resource('/api/messaging/email/templatevariable/:id/', {}, {
        query: {
            method: 'GET',
            // Because the API sends an object, we need this line
            isArray: false
        }
    });
}
