angular.module('app.base').controller('sidebarController', sidebarController);

sidebarController.$inject = ['$scope'];
function sidebarController($scope) {
    $scope.$on('$includeContentLoaded', () => {
        Layout.initSidebar(); // init sidebar
    });
}
