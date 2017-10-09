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
        compile: tElement => {
            return (scope, element) => {
                const elm = element[0];

                const check = () => {
                    if (scope.vm.hasOwnProperty('widgetInfo')) {
                        const maxHeight = (elm.offsetHeight === elm.scrollHeight);
                        // In certain cases the combined values won't be more than
                        // the scrollHeight eventhough we've reached the bottom.
                        // So for those cases we subtract 11 from the scrollHeight
                        // which is roughly equal to the height of the scroll indicator.
                        const endReached = (elm.offsetHeight + elm.scrollTop >= elm.scrollHeight - 11);

                        // Show the scroll indicator if we've:
                        // Reached the end of the scrollable area
                        // or if our widget is expanded and already at max-height.
                        scope.vm.showFade = !endReached || (maxHeight && scope.vm.widgetInfo.expandHeight);
                    }
                };

                const appliedCheck = () => {
                    scope.$apply(check);
                };

                element.bind('scroll', appliedCheck);

                $timeout(check, 500);

                angular.element($window).bind('resize', appliedCheck);
            };
        },
    };
}
