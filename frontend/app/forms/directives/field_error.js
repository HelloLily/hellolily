angular.module('app.forms.directives').directive('fieldError', fieldError);

function fieldError() {
    return {
        restrict: 'E',
        scope: {
            form: '=',
            field: '@',
            index: '='
        },
        templateUrl: 'forms/directives/field_error.html',
        controller: FieldErrorController,
        controllerAs: 'vm',
        bindToController: true
    }
}

function FieldErrorController() {
    var vm = this;

    var field = vm.field;

    // Related field names have an index at the end, so add the index if it's given
    if (vm.hasOwnProperty('index')) {
        field += '-' + vm.index;
    }

    vm.full_field = field;
}
