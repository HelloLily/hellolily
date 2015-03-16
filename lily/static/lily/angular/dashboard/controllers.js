/**
 * contactControllers is a container for all contact related Controllers
 */
angular.module('dashboardControllers', [
    'dashboardDirectives',
    'ui.slimscroll'
])

.controller('DashboardController', ['$scope', function($scope) {

    }])

.controller('UnreadEmailController', [
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
