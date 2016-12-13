angular.module('app.utils.directives').directive('passwordConfirmation', PasswordConfirmationDirective);

PasswordConfirmationDirective.$inject = [];
function PasswordConfirmationDirective() {
    return {
        restrict: 'E',
        templateUrl: 'utils/directives/password_confirmation.html',
        transclude: true,
        link: function(scope, element, attrs, collapsableCtrl) {
            djangoPasswordStrength.initListeners(element);
        },
    };
}
