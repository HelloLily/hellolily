angular.module('app.forms.directives').directive('formPortlet', formPortlet);

function formPortlet() {
    return {
        restrict: 'E',
        scope: {
            title: '@'
        },
        transclude: true,
        templateUrl: 'forms/directives/portlet.html'
    }
}
