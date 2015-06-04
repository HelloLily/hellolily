/**
 * Directive give a nice formatting on input elements.
 *
 * It makes sure that the value of the ngModel on the scope has a nice
 * formatting for the user
 */
angular.module('app.directives').directive('dateFormatter', dateFormatter);

dateFormatter.$inject = ['dateFilter'];
function dateFormatter(dateFilter) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            ngModel.$formatters.push(function(value) {
                if (value) {
                    return dateFilter(value, attrs.dateFormatter);
                }
            })
        }
    }
}
