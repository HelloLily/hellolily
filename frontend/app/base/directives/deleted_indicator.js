angular.module('app.directives').directive('deletedIndicator', deletedIndicator);
function deletedIndicator() {
    return {
        restrict: 'E',
        scope: {
            object: '<',
            field: '@',
        },
        templateUrl: 'base/directives/deleted_indicator.html',
        transclude: true,
    };
}
