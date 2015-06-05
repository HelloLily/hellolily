angular.module('app.deals.directives').directive('dealListWidget', DealListWidgetDirective);

function DealListWidgetDirective () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            addLink: '@'
        },
        templateUrl: 'deals/directives/list_widget.html'
    }
}
