angular.module('app.forms.directives').directive('formPortlet', formPortlet);

function formPortlet() {
    return {
        restrict: 'E',
        scope: {
            portletTitle: '@',
            collapsable: '=',
            position: '=',
        },
        transclude: true,
        templateUrl: 'forms/directives/portlet.html',
        controller: FormPortletController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

FormPortletController.$inject = ['$rootScope', '$scope'];
function FormPortletController($rootScope, $scope) {
    const vm = this;

    vm.sidebar = $rootScope.$$childHead.settings.email.sidebar.form;
}
