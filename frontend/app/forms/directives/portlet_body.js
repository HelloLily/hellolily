angular.module('app.forms.directives').directive('formPortletBody', formPortletBody);

function formPortletBody() {
    return {
        restrict: 'E',
        scope: {},
        transclude: true,
        templateUrl: 'forms/directives/portlet_body.html'
    }
}
