/**
 * Directive for a confirmation box before the delete in the detail
 * view happens
 */
angular.module('app.directives').directive('detailDelete', detailDelete);

detailDelete.$inject = ['$state'];
function detailDelete ($state) {
    return {
        restrict: 'A',
        link: function (scope, elem, attrs) {

            $(elem).click(function () {
                if (confirm('You are deleting! Are you sure ?')) {
                    $state.go('.delete');
                }
            });
        }
    }
}
