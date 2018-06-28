angular.module('app.directives').directive('callerInfo', callerInfo);

function callerInfo() {
    return {
        restrict: 'E',
        scope: true,
        templateUrl: 'base/directives/caller_info.html',
        controller: CallerInfoController,
        controllerAs: 'vm',
        transclude: true,
        bindToController: true,
    };
}

CallerInfoController.$inject = ['$state', 'Account', 'Call'];
function CallerInfoController($state, Account, Call) {
    const vm = this;
    let phoneNumber = '';

    vm.fetchCallerInfo = fetchCallerInfo;

    function fetchCallerInfo() {
        // Get the latest call of the current user based on the internal number.
        Call.getLatestCall().$promise.then(callInfo => {
            const call = callInfo.call;

            if (call) {
                phoneNumber = call.caller.number;
                // There was a call for the current user, so try to find an account or contact with the given number.
                Account.searchByPhoneNumber({number: call.caller.number}).$promise.then(response => {
                    if (response.data.account) {
                        // Account found so redirect to the account.
                        $state.go('base.accounts.detail', {id: response.data.account.id}, {reload: true});
                    } else if (response.data.contact) {
                        // Contact found so redirect to the contact.
                        $state.go('base.contacts.detail', {id: response.data.contact.id}, {reload: true});
                    } else {
                        // No account or contact found so redirect to create account form.
                        $state.go(
                            'base.accounts.create',
                            {
                                'name': call.caller.name,
                                'phone_number': call.caller.number,
                            },
                            {reload: true}
                        );
                    }
                });
            } else {
                toastr.error('No calls for you right now', 'No calls');
            }
        });

        // Track clicking on the caller info button in Segment.
        analytics.track('caller-info-click', {
            'phone_number': phoneNumber,
        });
    }
}
