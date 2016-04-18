angular.module('app.directives').directive('ngSpinnerBar', ngSpinnerBar);

ngSpinnerBar.$inject = ['$rootScope'];
function ngSpinnerBar($rootScope) {
    return {
        link: function(scope, element, attrs) {
            // By default hide the spinner bar.
            element.addClass('hide');

            // Display the spinner bar whenever the route changes (the content part started loading).
            $rootScope.$on('$stateChangeStart', function() {
                element.removeClass('hide');
            });

            // Hide the spinner bar on route change success (after the content loaded).
            $rootScope.$on('$stateChangeSuccess', function() {
                element.addClass('hide');
                // Remove page loading indicator.
                $('body').removeClass('page-on-load');
            });

            // Handle errors.
            $rootScope.$on('$stateNotFound', function() {
                element.addClass('hide');
            });

            $rootScope.$on('$stateChangeError', function() {
                element.addClass('hide');
            });
        },
    };
}
