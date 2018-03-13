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
            billingInfo: ['Billing', Billing => Billing.getBillingInfo().$promise],
            countries: ['Country', Country => Country.getList()],
        },
    });
}


angular.module('app.base').controller('BillingOverviewController', BillingOverviewController);

BillingOverviewController.$inject = ['$filter', '$scope', '$state', '$window', 'Billing', 'Settings', 'billingInfo', 'countries'];
function BillingOverviewController($filter, $scope, $state, $window, Billing, Settings, billingInfo, countries) {
    const vm = this;

    Settings.page.setAllTitles('list', 'billing');

    vm.card = billingInfo.card;
    vm.customer = billingInfo.customer;
    vm.subscription = billingInfo.subscription;
    vm.plan = billingInfo.plan;
    vm.invoices = billingInfo.invoices;
    vm.paymentMethod = billingInfo.customer.payment_method ? billingInfo.customer.payment_method.type : null;

    vm.downloadInvoice = downloadInvoice;
    vm.cancelSubscription = cancelSubscription;
    vm.updateCard = updateCard;

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

    function _getCountryName(countryCode) {
        const filtered = countries.filter(country => country.value === countryCode);

        return filtered.length ? filtered[0].display_name : '';
    }

    function updateCard() {
        Billing.getHostedPage({action: 'update_card'}).$promise.then(response => {
            $window.location.href = response.url;
        });
    }
}

