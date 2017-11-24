angular.module('app.base').directive('pageHeader', pageHeader);

pageHeader.$inject = [];
function pageHeader() {
    return {
        restrict: 'E',
        scope: true,
        templateUrl: 'base/header.html',
        controller: PageHeaderController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

PageHeaderController.$inject = ['$scope'];
function PageHeaderController($scope) {
    const vm = this;

    vm.billingEnabled = window.billingEnabled;

    vm.openForm = openForm;

    $scope.$on('$includeContentLoaded', () => {
        Layout.initHeader(); // init header
    });

    function openForm(form) {
        form.$show();
    }
}
