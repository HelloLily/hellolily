angular.module('app.forms.directives').directive('formPortletBody', formPortletBody);

function formPortletBody() {
    return {
        restrict: 'E',
        scope: {},
        transclude: true,
        templateUrl: 'forms/directives/portlet_body.html',
        controller: FormBodyPortletController,
        controllerAs: 'vm'
    }
}

FormBodyPortletController.$inject = ['$rootScope'];
function FormBodyPortletController($rootScope) {
    var vm = this;
    vm.sideBar = $rootScope.$$childHead.emailSettings.sideBar;
}
