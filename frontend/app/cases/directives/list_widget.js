angular.module('app.cases.directives').directive('caseListWidget', CaseListWidget);

function CaseListWidget() {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            title: '@',
            list: '=',
            height: '=',
            addLink: '@',
        },
        templateUrl: 'cases/directives/list_widget.html',
        controller: CaseListWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

CaseListWidgetController.$inject = [];
function CaseListWidgetController() {
    var vm = this;

    angular.forEach(vm.list, function(lilyCase) {
        lilyCase.collapsed = true;
    });
}

