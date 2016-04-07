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
        templateUrl: function(elem, attrs) {
            var templateUrl = '';

            if (attrs.collapsable) {
                templateUrl = 'forms/directives/collapsable_portlet.html';
            } else {
                templateUrl = 'forms/directives/portlet.html';
            }

            return templateUrl;
        },
        controller: FormPortletController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

FormPortletController.$inject = ['$rootScope', '$scope'];
function FormPortletController($rootScope, $scope) {
    var vm = this;

    // In certain forms we want to collapse all portlets except a certain one.
    if (typeof $scope.$parent.vm.startsAt !== 'undefined') {
        // Collapse all portlets except the given portlet.
        vm.collapsed = vm.position !== $scope.$parent.vm.startsAt;
    }

    if (vm.collapsable) {
        $scope.$parent.vm.formPortlets[vm.position].portlet = vm;
    }

    vm.sidebar = $rootScope.$$childHead.settings.email.sidebar.form;
}
