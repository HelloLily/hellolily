angular.module('app.directives').directive('onModEnterKey', onModEnterKey);

function onModEnterKey() {
    return function(scope, element, attrs) {
        element.bind('keydown keypress', function(event) {
            if (navigator.userAgent.indexOf('Mac OS X') !== -1) {
                if (event.which === 13 && event.metaKey) {
                    scope.$apply(function() {
                        scope.$eval(attrs.onModEnterKey);
                    });

                    event.preventDefault();
                }
            } else {
                if (event.which === 13 && event.ctrlKey) {
                    scope.$apply(function() {
                        scope.$eval(attrs.onModEnterKey);
                    });

                    event.preventDefault();
                }
            }
        });
    };
}
