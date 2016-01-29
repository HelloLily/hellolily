angular.module('app.email.services').factory('EmailLabel', EmailLabel);

EmailLabel.$inject = ['$resource'];
function EmailLabel($resource) {
    var _emailLabel = $resource(
        '/api/messaging/email/label/:id/',
        {},
        {
            query: {
                isArray: false,
            },
        }
    );
    return _emailLabel;
}
