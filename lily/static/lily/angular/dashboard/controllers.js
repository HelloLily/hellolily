/**
 * contactControllers is a container for all contact related Controllers
 */
var dashboard = angular.module('dashboardControllers', [
    'dashboardDirectives',
    'ui.slimscroll'
]);

dashboard.controller('DashboardController', ['$scope', function($scope) {

    }]);

dashboard.controller('UnreadEmailController', [
        '$scope',

        'EmailAccount',
        'EmailMessage',
        function($scope, EmailAccount, EmailMessage) {
            var filterquery = ['read:false'];

            EmailMessage.SEARCH.get({
                filterquery: filterquery
            }, function(data) {
                $scope.emailMessages = data.hits;
                //$scope.table.totalItems = data.total;
            });
    }]);

dashboard.controller('MyCasesController', ['$scope', 'Case', function($scope, Case){
        Case.getMyCasesWidget().then(function (data) {
            $scope.mycases = data;
        });
}]);
