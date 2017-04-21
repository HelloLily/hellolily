angular.module('app.directives').directive('objectLimit', objectLimit);

function objectLimit() {
    return {
        restrict: 'A',
        scope: true,
        link: (scope, element, attrs) => {
            if (currentUser.limitReached[attrs.objectLimit]) {
                element.addClass('disabled');
            }
        },
    };
}
