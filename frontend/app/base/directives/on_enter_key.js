angular.module('app.directives').directive('onEnterKey', onEnterKey);

function onEnterKey() {
    return function(scope, element, attrs) {
        element.bind('keydown keypress', function(event) {
            if (event.which === 13) {
                scope.$apply(function() {
                    scope.$eval(attrs.onEnterKey);
                });

                event.preventDefault();
            }
        });
    };
}
