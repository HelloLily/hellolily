angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: DealDeleteController,
            },
        },
    });
}

angular.module('app.deals').controller('DealDeleteController', DealDeleteController);

DealDeleteController.$inject = ['$http', '$state', '$stateParams'];
function DealDeleteController($http, $state, $stateParams) {
    var id = $stateParams.id;
    var req = {
        method: 'POST',
        url: '/deals/delete/' + id + '/',
        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
    };

    $http(req).
        success(function(data, status, headers, config) {
            $state.go('base.deals');
        }).
        error(function(data, status, headers, config) {
            $state.go('base.deals');
        });
}
