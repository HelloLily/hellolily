angular.module('app.preferences').config(billingOverviewConfig);

billingOverviewConfig.$inject = ['$stateProvider'];
function billingOverviewConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.billing', {
        url: '/billing',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/billing/overview.html',
                controller: BillingOverviewController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            billingInfo: ['Billing', (Billing) => {
                return Billing.getBillingInfo().$promise;
            }],
        },
    });
}


angular.module('app.base').controller('BillingOverviewController', BillingOverviewController);

BillingOverviewController.$inject = ['$scope', '$state', '$window', 'Billing', 'billingInfo'];
function BillingOverviewController($scope, $state, $window, Billing, billingInfo) {
    var vm = this;

    vm.card = billingInfo.card;
    vm.customer = billingInfo.customer;
    vm.subscription = billingInfo.subscription;
    vm.plan = billingInfo.plan;
    vm.invoices = billingInfo.invoices;
    vm.paymentMethod = billingInfo.customer.payment_method ? billingInfo.customer.payment_method.type : null;

    vm.downloadInvoice = downloadInvoice;
    vm.cancelSubscription = cancelSubscription;
    vm.getTrialRemaining = getTrialRemaining;

    function downloadInvoice(invoiceId) {
        Billing.downloadInvoice({'invoice_id': invoiceId}).$promise.then((response) => {
            $window.location.assign(response.url);
        });
    }

    function cancelSubscription() {
        swal({
            title: messages.alerts.preferences.subscriptionCancelTitle,
            html: messages.alerts.preferences.subscriptionCancelText,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f3565d',
            confirmButtonText: messages.alerts.preferences.confirmButtonText,
        }).then((isConfirm) => {
            if (isConfirm) {
                Billing.cancel().$promise.then((response) => {
                    if (response.success) {
                        $state.reload();
                    } else {
                        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                    }
                }, (error) => {
                    toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                });
            }
        }).done();
    }

    function getTrialRemaining(trialEndDate) {
        var trialEnd = moment.unix(trialEndDate);

        return trialEnd.fromNow(true);
    }
}

