angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/detail.html',
                controller: DealDetailController
            }
        },
        ncyBreadcrumb: {
            label: '{{ deal.name }}'
        }
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$http', '$scope', '$stateParams', 'DealDetail', 'DealStages'];
function DealDetailController ($http, $scope, $stateParams, DealDetail, DealStages) {
    $scope.conf.pageTitleBig = 'Deal detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    var id = $stateParams.id;

    $scope.deal = DealDetail.get({id: id});
    $scope.dealStages = DealStages.query();

    /**
     * Change the state of a deal
     */
    $scope.changeState = function(stage) {
        var newStage = stage;

        var req = {
            method: 'POST',
            url: '/deals/update/stage/' + $scope.deal.id + '/',
            data: 'stage=' + stage,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.stage = newStage;
                $scope.deal.stage_name = data.stage;
                if(data.closed_date !== undefined){
                    $scope.deal.closing_date = data.closed_date;
                }
                $scope.loadNotifications();
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };

    /**
     * Archive a deal
     */
    $scope.archive = function(id) {
        var req = {
            method: 'POST',
            url: '/deals/archive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.archived = true;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };

    /**
     * Unarchive a deal
     */
    $scope.unarchive = function(id) {
        var req = {
            method: 'POST',
            url: '/deals/unarchive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $scope.deal.archived = false;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    };
}
