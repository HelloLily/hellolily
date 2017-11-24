angular.module('app.preferences').config(subscriptionConfig);

subscriptionConfig.$inject = ['$stateProvider'];
function subscriptionConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.billing.edit', {
        url: '/change/',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/billing/edit_subscription.html',
                controller: EditSubscriptionController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            plans: ['Billing', (Billing) => {
                return Billing.getPlans().$promise;
            }],
        },
    });
}


angular.module('app.base').controller('EditSubscriptionController', EditSubscriptionController);

EditSubscriptionController.$inject = ['$scope', '$state', '$window', 'Billing', 'HLForms', 'plans'];
function EditSubscriptionController($scope, $state, $window, Billing, HLForms, plans) {
    const vm = this;

    vm.subscription = plans.subscription;
    vm.currentPlan = plans.current_plan;

    if (vm.currentPlan) {
        vm.selectedPlan = plans.current_plan.id;
    } else {
        vm.selectedPlan = null;
    }

    vm.plans = plans.plans;

    vm.saveSubsciption = saveSubsciption;
    vm.cancelEditSubscription = cancelEditSubscription;

    function saveSubsciption(form) {
        HLForms.blockUI();

        Billing.patch({'plan_id': vm.selectedPlan}).$promise.then(response => {
            if (response.url) {
                $window.location.href = response.url;
            } else {
                if (response.success) {
                    // Free plan so just redirect back to overview page.
                    toastr.success(messages.notifications.subscriptionUpdated, messages.notifications.successTitle);
                    $state.go('base.preferences.admin.billing');
                } else {
                    toastr.error(messages.notifications.subscriptionError, messages.notifications.errorTitle);
                }
            }
        }, error => {
            Metronic.unblockUI();
        });
    }

    function cancelEditSubscription() {
        $state.go('base.preferences.admin.billing');
    }
}

