angular.module('app.base').controller('headerController', headerController);

headerController.$inject = ['$scope'];
function headerController($scope) {
    $scope.$on('$includeContentLoaded', function() {
        Layout.initHeader(); // init header
    });
}
