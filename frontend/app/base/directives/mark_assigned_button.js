angular.module('app.directives').directive('markAssignedButton', markAssignedButton);

function markAssignedButton() {
    return {
        restrict: 'A',
        scope: {
            callback: '&',
        },
        link: function(scope, element, attrs) {
            element.on('click', function() {
                // Get the closest table row.
                element.closest('.newly-assigned').fadeOut(500, function() {
                    // Mark the item as assigned.
                    scope.callback();
                });
            });
        },
    };
}
