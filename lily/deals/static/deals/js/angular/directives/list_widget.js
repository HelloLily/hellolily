(function() {
    'use strict';

    /**
     * Deals list widget
     */
    angular.module('app.deals.directives').directive('dealListWidget', DealListWidget);

    function DealListWidget() {
        return {
            restrict: 'E',
            replace: true,
            scope: {
                title: '@',
                list: '=',
                height: '=',
                addLink: '@'
            },
            templateUrl: 'deals/directives/list-widget.html'
        }
    }
})();
