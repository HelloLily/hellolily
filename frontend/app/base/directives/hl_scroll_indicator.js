/**
 * HL directive to add a scrolling indicator to widgets with a specific height.
 *
 */
angular.module('app.directives').directive('hlScrollIndicator', hlScrollIndicator);

hlScrollIndicator.$inject = ['$timeout', '$window'];

function hlScrollIndicator($timeout, $window) {
    return {
        restrict: 'A',
        scope: true,
        compile: function(tElement) {
            return function(scope, element) {
                var elm = element[0];
                // Check if the bottom of an element is reached and set the
                // showFade variable to false.
                var check = function() {
                    scope.vm.showFade = !(elm.offsetHeight + elm.scrollTop >= elm.scrollHeight);
                };

                var appliedCheck = function() {
                    scope.$apply(check);
                };

                element.bind('scroll', appliedCheck);

                check();

                $timeout(check, 500);

                angular.element($window).bind('resize', appliedCheck);
            };
        },
    };
}
