angular.module('app.dashboard.directives').directive('queueSize', queueSizeDirective);

function queueSizeDirective (){
    return {
        scope: {},
        templateUrl: 'dashboard/directives/queuesize.html',
        controller: QueueSizeController
    }
}

QueueSizeController.$inject = ['$filter', '$http', '$interval', '$scope'];
function QueueSizeController ($filter, $http, $interval, $scope) {
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
