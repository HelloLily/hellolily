angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: CaseDeleteController,
            },
        },
    });
}

angular.module('app.cases').controller('CaseDeleteController', CaseDeleteController);

CaseDeleteController.$inject = ['$http', '$state', '$stateParams'];
function CaseDeleteController($http, $state, $stateParams) {
    var id = $stateParams.id;

    var req = {
        method: 'POST',
        url: '/cases/delete/' + id + '/',
        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
    };

    $http(req).
        success(function(data, status, headers, config) {
            $state.go('base.cases');
        }).
        error(function(data, status, headers, config) {
            $state.go('base.cases');
        });
}
