angular.module('app.dashboard.directives').directive('simpleWidget', simpleWidget);

function simpleWidget() {
    return {
        restrict: 'E',
        scope: true,
        templateUrl: 'base/directives/simple_widget.html',
        controllerAs: 'vm',
        bindToController: true,
        transclude: {
            widgetHeader: 'widgetHeader',
            widgetBody: 'widgetBody',
        },
    };
}
