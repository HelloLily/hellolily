/**
 * dashboardControllers is a container for all contact related Controllers
 */
var dashboard = angular.module('dashboardControllers', [
    'dashboardDirectives',
    'chart.js',
    'ui.slimscroll',
    'UserServices'
]);

dashboard.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.dashboard', {
        url: '/',
        views: {
            '@': {
                templateUrl: 'dashboard/base.html',
                controller: 'DashboardController'
            }
        },
        ncyBreadcrumb: {
            label: 'Dashboard'
        }
    });
}]);

dashboard.controller('DashboardController', [
    '$scope',
    function ($scope) {
        $scope.conf.pageTitleBig = 'Dashboard';
        $scope.conf.pageTitleSmall = 'statistics and usage';
    }
]);

dashboard.controller('UnreadEmailController', [
    '$scope',
    'EmailAccount',
    'EmailMessage',
    function($scope, EmailAccount, EmailMessage) {

        var filterquery = ['read:false AND label_id:INBOX'];

        EmailMessage.SEARCH.get({
            filterquery: filterquery
        }, function (data) {
            $scope.emailMessages = data.hits;
        });
    }
]);

dashboard.controller('MyCasesController', [
    '$scope',
    'Case',
    function ($scope, Case) {
        Case.getMyCasesWidget().then(function (data) {
            $scope.mycases = data;
        });
    }
]);

dashboard.controller('CallbackRequestsController', [
    '$scope',
    'Case',
    function ($scope, Case) {
        Case.getCallbackRequests().then(function (data) {
            $scope.callbackRequests = data.callbackRequests;
        });
    }
]);

/**
 * Controller for the UnassignedCases dashboard widget(s), which shows
 * a widget per team for unassigned cases.
 */
dashboard.controller('UnassignedCasesController', [
    '$scope',
    'UserTeams',
    'UnassignedTeamCases',
    function($scope, UserTeams, UnassignedTeamCases) {

        UserTeams.query(function(teams) {
            $scope.teams = teams;

            teams.forEach(function(team, i) {
                UnassignedTeamCases.query({teamId: team.id}, function(cases) {
                    teams[i].cases = cases;
                })
            })
        })
    }
]);

/**
 * Controller for superuser to check the queue size of worker 1
 */
dashboard.controller('QueueSizeController', [
    '$filter',
    '$http',
    '$interval',
    '$scope',
    function($filter, $http, $interval, $scope) {

        $scope.currentUser = currentUser;
        if (!currentUser.isSuperUser) return;
        $scope.labels = [];
        $scope.series = ['Queue Size'];
        $scope.data = [[]];
        $scope.options = {
            animation: false
        };
        $scope.queueName = 'queue1';

        var getQueueInfo = function() {
            $http.get('/api/utils/queues/' + $scope.queueName + '/').then(function(data){
                $scope.labels.push($filter('date')(Date.now(), 'H:mm:ss'));
                $scope.data[0].push(data.data.size);
                if ($scope.data[0].length > 15) {
                    $scope.data[0].shift();
                    $scope.labels.shift();
                }
                $scope.totalSize = data.data.total_messages;
            });
        };
        //Fetch again every 10 seconds
        getQueueInfo();
        var stop = $interval(getQueueInfo, 10000);

        $scope.$on('$destroy', function() {
            // Make sure that the interval is destroyed too
            if (angular.isDefined(stop)) {
                $interval.cancel(stop);
                stop = undefined;
            }
        });
    }
]);

