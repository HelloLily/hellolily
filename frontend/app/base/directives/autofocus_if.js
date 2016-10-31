angular.module('app.directives').directive('autofocusIf', autofocusIf);

function autofocusIf() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            scope.$watch(function() {
                return scope.$eval(attrs.autofocusIf);
            }, function(bool) {
                if (bool === true) {
                    element[0].focus();
                }
            });
        },
    };
}
