angular.module('app.forms.directives').directive('formGroup', formGroup);

function formGroup() {
    return {
        restrict: 'E',
        scope: {
            labelId: '@',
            labelTitle: '@',
            labelChar: '@',
            field: '=',
            required: '@',
        },
        transclude: true,
        templateUrl: 'forms/directives/group.html',
        controller: FormGroupController,
        controllerAs: 'vm',
    };
}

FormGroupController.$inject = ['$rootScope'];
function FormGroupController($rootScope) {
    var vm = this;
    vm.sidebar = $rootScope.$$childHead.settings.email.sidebar.form;
}
