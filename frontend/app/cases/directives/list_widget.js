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
        controller: FormPortletController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

FormPortletController.$inject = [];
function FormPortletController() {
    var vm = this;

    console.log(vm.list);

    angular.forEach(vm.list, function(lilyCase) {
        lilyCase.collapsed = true;
    });
}

