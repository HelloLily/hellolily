angular.module('app.forms.directives').directive('formPortlet', formPortlet);

function formPortlet() {
    return {
        restrict: 'E',
        scope: {
            title: '@'
        },
        transclude: true,
        templateUrl: 'forms/directives/portlet.html',
        controller: FormPortletController,
        controllerAs: 'vm'
    }
}

FormPortletController.$inject = ['$rootScope'];
function FormPortletController($rootScope) {
    var vm = this;
    vm.sidebar = $rootScope.$$childHead.emailSettings.sidebar.form;
}
