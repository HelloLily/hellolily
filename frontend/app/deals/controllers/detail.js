angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/detail.html',
                controller: DealDetailController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: '{{ deal.name }}',
        },
        resolve: {
            deal: ['DealDetail', '$stateParams', function(DealDetail, $stateParams) {
                var id = $stateParams.id;
                return DealDetail.get({id: id}).$promise;
            }],
        },
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$http', '$scope', 'DealStages', 'deal'];
function DealDetailController($http, $scope, DealStages, deal) {
    var vm = this;

    $scope.conf.pageTitleBig = 'Deal detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    vm.deal = deal;
    vm.dealStages = DealStages.query();

    vm.changeState = changeState;
    vm.archive = archive;
    vm.unarchive = unarchive;

    //////

    //
    /**
     * Change the state of a deal
     */
    function changeState(stage) {
        var req = {
            method: 'POST',
            url: '/deals/update/stage/' + vm.deal.id + '/',
            data: 'stage=' + stage,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
        };

        $http(req).
            success(function(data) {
                vm.deal.stage = stage;
                vm.deal.stage_name = data.stage;
                vm.deal.closed_date = data.closed_date;

                $scope.loadNotifications();
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Archive a deal
     */
    function archive(id) {
        var req = {
            method: 'POST',
            url: '/deals/archive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.deal.archived = true;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Unarchive a deal
     */
    function unarchive(id) {
        var req = {
            method: 'POST',
            url: '/deals/unarchive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.deal.archived = false;
            }).
            error(function(data, status, headers, config) {
                // Request failed proper error?
            });
    }
}
