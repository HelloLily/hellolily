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
                var check = function() {
                    var maxHeight = (elm.offsetHeight === elm.scrollHeight);
                    // In certain cases the combined values won't be more than
                    // the scrollHeight eventhough we've reached the bottom.
                    // So for those cases we subtract 11 from the scrollHeight
                    // which is roughly equal to the height of the scroll indicator.
                    var endReached = (elm.offsetHeight + elm.scrollTop >= elm.scrollHeight - 11);

                    // Show the scroll indicator if we've:
                    // Reached the end of the scrollable area
                    // or if our widget is expanded and already at max-height.
                    scope.vm.showFade = !endReached || (maxHeight && scope.vm.widgetInfo.expandHeight);
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
