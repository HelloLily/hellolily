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
    $scope.$on('$includeContentLoaded', function() {
        Layout.initHeader(); // init header
    });
}
