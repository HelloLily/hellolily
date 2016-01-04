/**
 * HL specific pagination directive for generic pagination use.
 *
 * @param values {Object}: Contains table information used to set up pagination.
 *
 * Example:
 * <hl-pagination values="vm.table"></hl-pagination>
 */
angular.module('app.directives').directive('hlPagination', hlPagination);

function hlPagination() {
    return {
        restrict: 'E',
        scope: {
            values: '=',
        },
        templateUrl: 'base/directives/hl_pagination.html',
    };
}
