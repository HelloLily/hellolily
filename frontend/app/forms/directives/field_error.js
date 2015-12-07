angular.module('app.forms.directives').directive('fieldError', fieldError);

function fieldError() {
    return {
        restrict: 'E',
        scope: {
            form: '=',
            field: '@',
            index: '=',
        },
        templateUrl: 'forms/directives/field_error.html',
        controller: FieldErrorController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

function FieldErrorController() {
}
