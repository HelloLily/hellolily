/**
 * checkbox Directive makes a nice uniform checkbox and binds to a model
 *
 * @param model object: model to bind checkbox with
 *
 * Example:
 * <checkbox model="table.visibility.name">Name</checkbox>
 */
angular.module('app.directives').directive('checkbox', checkbox);

function checkbox () {
    return {
        restrict: 'E',
        replace: true,
        transclude: true,
        scope: {
            model: '='
        },
        templateUrl: 'base/directives/checkbox.html'
    }
}
