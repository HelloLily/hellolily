angular.module('app.preferences').config(subscriptionConfig);

subscriptionConfig.$inject = ['$stateProvider'];
function subscriptionConfig($stateProvider) {
    let view = {
        '@base.preferences': {
            templateUrl: 'preferences/admin/billing/chargebee.html',
            controller: EditSubscriptionController,
            controllerAs: 'vm',
        },
    };

    $stateProvider.state('base.preferences.admin.billing.card', {
        url: '/card/',
        views: view,
        resolve: {
            hostedPage: ['Billing', (Billing) => {
                return Billing.getHostedPage({action: 'update_card'}).$promise;
            }],
        },
    });
}

angular.module('app.base').controller('EditSubscriptionController', EditSubscriptionController);

EditSubscriptionController.$inject = ['$scope', '$state', '$window', 'Billing', 'hostedPage'];
function EditSubscriptionController($scope, $state, $window, Billing, hostedPage) {
    $window.location.href = hostedPage.url;
}

