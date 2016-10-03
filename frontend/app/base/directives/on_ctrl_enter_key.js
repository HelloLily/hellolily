angular.module('app.directives').directive('onCtrlEnterKey', onCtrlEnterKey);

function onCtrlEnterKey() {
    return function(scope, element, attrs) {
        element.bind('keydown keypress', function(event) {
            if (event.which === 13 && event.ctrlKey) {
                scope.$apply(function() {
                    scope.$eval(attrs.onCtrlEnterKey);
                });

                event.preventDefault();
            }
        });
    };
}
