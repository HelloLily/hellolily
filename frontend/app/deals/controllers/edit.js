angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function (elem, attr) {
                    return '/deals/update/' + elem.id + '/';
                },
                controller: DealEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.deals').controller('DealEditController', DealEditController);

DealEditController.$inject = ['$scope', '$stateParams', 'Settings', 'DealDetail'];
function DealEditController ($scope, $stateParams, Settings, DealDetail) {
    var id = $stateParams.id;
    var dealPromise = DealDetail.get({id: id}).$promise;

    dealPromise.then(function(deal) {
        $scope.deal = deal;
        Settings.page.setAllTitles('edit', deal.name);
    })
}
