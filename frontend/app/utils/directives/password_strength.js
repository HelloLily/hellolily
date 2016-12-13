angular.module('app.utils.directives').directive('passwordStrength', PasswordStrengthDirective);

PasswordStrengthDirective.$inject = [];
function PasswordStrengthDirective() {
    return {
        restrict: 'E',
        templateUrl: 'utils/directives/password_strength.html',
        transclude: true,
        link: function(scope, element, attrs, collapsableCtrl) {
            djangoPasswordStrength.initListeners(element);
        },
    };
}
