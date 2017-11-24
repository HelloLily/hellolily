angular.module('app.directives').directive('markAssignedButton', markAssignedButton);

function markAssignedButton() {
    return {
        restrict: 'A',
        scope: {
            callback: '&',
        },
        link: (scope, element, attrs) => {
            element.on('click', function() {
                // Get the closest table row.
                element.closest('.newly-assigned').fadeOut(500, () => {
                    // Mark the item as assigned.
                    scope.callback();
                });
            });
        },
    };
}
