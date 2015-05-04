(function() {
    'use strict';

    angular.module('app.dashboard.directives', []);

    /**
     * Unread Email Widget
     */
    angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmail);

    function unreadEmail () {
        return {
            templateUrl: 'dashboard/unreademail.html',
            controller: 'UnreadEmail',
            controllerAs: 'vm'
        }
    }

    angular.module('app.dashboard.directives').controller('UnreadEmail', UnreadEmail);

    UnreadEmail.$inject = ['$scope', 'EmailMessage', 'Cookie'];
    function UnreadEmail ($scope, EmailMessage, Cookie) {

        Cookie.prefix ='unreadEmailWidget';

        var vm = this;
        vm.table = {
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'sent_date'  // string: current sorted column
            }),
            items: []
        };
        var filterQuery = ['read:false AND label_id:INBOX'];

        activate();

        //////

        function activate() {
            _getMessages();
            _watchTable();
        }

        function _getMessages () {
            EmailMessage.getDashboardMessages(
                vm.table.order.column,
                vm.table.order.ascending,
                filterQuery
            ).then(function (messages) {
                vm.table.items = messages;
            });
        }

        function _watchTable() {
            $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
                _getMessages();
            })
        }
    }

    /**
     * CallbackRequests widget
     */
    angular.module('app.dashboard.directives').directive('callbackRequests', callbackRequests);

    function callbackRequests () {
        return {
            templateUrl: 'dashboard/callbackrequests.html',
            controller: 'CallbackRequests'
        }
    }

    angular.module('app.dashboard.directives').controller('CallbackRequests', CallbackRequests);

    CallbackRequests.$inject = ['$scope', 'Case'];
    function CallbackRequests ($scope, Case) {
        Case.getCallbackRequests().then(function (data) {
            $scope.callbackRequests = data.callbackRequests;
        });
    }

    /**
     * Controller for the UnassignedCases dashboard widget(s), which shows
     * a widget per team for unassigned cases.
     */
    angular.module('app.dashboard.directives').directive('unassignedCases', unassignedCases);

    function unassignedCases () {
        return {
            templateUrl: 'dashboard/unassignedcases.html',
            controller: 'UnassignedCases'
        }
    }

    angular.module('app.dashboard.directives').controller('UnassignedCases', UnassignedCases);

    UnassignedCases.$inject = ['$http', '$scope', 'UserTeams', 'UnassignedTeamCases'];
    function UnassignedCases ($http, $scope, UserTeams, UnassignedTeamCases) {

        UserTeams.query(function(teams) {
            $scope.teams = teams;

            teams.forEach(function(team, i) {
                UnassignedTeamCases.query({teamId: team.id}, function(cases) {
                    teams[i].cases = cases;
                })
            })
        });

        $scope.assignToMe = function(teamObj, caseObj){
            var caseId = caseObj.id;

            if(confirm('Assign this case to yourself?')){
                var req = {
                    method: 'POST',
                    url: '/cases/update/assigned_to/' + caseId + '/',
                    data: 'assignee=' + $scope.currentUser.id,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
                };

                $http(req).
                    success(function(data, status, headers, config) {
                        $scope.mycases.push(caseObj);
                        var team = $scope.teams[$scope.teams.indexOf(teamObj)];
                        team.cases.splice(team.cases.indexOf(caseObj), 1);
                        $scope.loadNotifications();
                    }).
                    error(function(data, status, headers, config) {
                        // Request failed propper error?
                    });
            }
        };
    }

    /**
     * Queue size widget for superusers
     *
     * to check the queue size of worker 1
     */
    angular.module('app.dashboard.directives').directive('queueSize', queueSize);

    function queueSize (){
        return {
            templateUrl: 'dashboard/queue-size.html',
            controller: 'QueueSize'
        }
    }

    angular.module('app.dashboard.directives').controller('QueueSize', QueueSize);

    QueueSize.$inject = ['$filter', '$http', '$interval', '$scope'];
    function QueueSize ($filter, $http, $interval, $scope) {
        $scope.show = false;
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
                $scope.show = true;
            }, function() {
                $interval.cancel(stop);
                $scope.show = false;
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
})();
