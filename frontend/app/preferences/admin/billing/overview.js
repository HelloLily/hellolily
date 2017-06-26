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
            billingInfo: ['Billing', Billing => {
                return Billing.getBillingInfo().$promise;
            }],
            countries: ['Country', Country => {
                return Country.getList();
            }],
        },
    });
}


angular.module('app.base').controller('BillingOverviewController', BillingOverviewController);

BillingOverviewController.$inject = ['$filter', '$scope', '$state', '$window', 'Billing', 'billingInfo', 'countries'];
function BillingOverviewController($filter, $scope, $state, $window, Billing, billingInfo, countries) {
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
    vm.startTrial = startTrial;

    activate();

    ////

    function activate() {
        if (vm.customer.billing_address) {
            vm.customer.billing_address.country_display = _getCountryName(vm.customer.billing_address.country);
        }
    }

    function downloadInvoice(invoiceId) {
        Billing.downloadInvoice({'invoice_id': invoiceId}).$promise.then(response => {
            $window.location.assign(response.url);
        });
    }

    function cancelSubscription() {
        swal({
            title: messages.alerts.preferences.subscription.cancelTitle,
            html: messages.alerts.preferences.subscription.cancelText,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#f3565d',
            confirmButtonText: messages.alerts.preferences.confirmButtonText,
        }).then(isConfirm => {
            if (isConfirm) {
                Billing.cancel().$promise.then(response => {
                    if (response.success) {
                        $state.reload();
                    } else {
                        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                    }
                }, error => {
                    toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                });
            }
        }).done();
    }

    function startTrial() {
        swal({
            title: messages.alerts.preferences.subscription.trialStartTitle,
            html: messages.alerts.preferences.subscription.trialStartText,
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: messages.alerts.preferences.subscription.trialConfirm,
        }).then(isConfirm => {
            if (isConfirm) {
                Billing.startTrial().$promise.then(response => {
                    $window.location.reload();
                });
            }
        }).done();
    }

    function getTrialRemaining(trialEndDate) {
        let trialEnd = moment.unix(trialEndDate);

        return trialEnd.fromNow(true);
    }

    function _getCountryName(countryCode) {
        let filtered = countries.filter(country => {
            return country.value === countryCode;
        });

        return filtered.length ? filtered[0].display_name : '';
    }
}

