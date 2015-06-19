angular.module('app.forms.directives').directive('formGroup', formGroup);

function formGroup() {
    return {
        restrict: 'E',
        scope: {
            labelId: '@',
            labelTitle: '@',
            field: '='
        },
        transclude: true,
        templateUrl: 'forms/directives/group.html'
    }
}
