angular.module('app.cases.directives').directive('caseListWidget', CaseListWidget);
function CaseListWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            addLink: '@'
        },
        templateUrl: 'cases/directives/list_widget.html'
    }
}
