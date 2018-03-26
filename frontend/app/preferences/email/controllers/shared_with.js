angular.module('app.preferences.email.directives').directive('sharedWith', sharedWith);

function sharedWith() {
    return {
        restrict: 'E',
        replace: true,
        templateUrl: 'preferences/email/directives/shared_with.html',
    };
}
