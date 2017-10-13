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
    var vm = this;

    vm.fetchCallerInfo = fetchCallerInfo;

    function fetchCallerInfo() {
        // Get the latest call of the current user based on the internal number.
        Call.getLatestCall().$promise.then(function(callInfo) {
            var call = callInfo.call;

            if (call) {
                // There was a call for the current user, so try to find an account with the given number.
                Account.searchByPhoneNumber({number: call.caller.number}).$promise.then(function(response) {
                    if (response.data.accounts.length) {
                        // Account found so redirect to the account.
                        $state.go('base.accounts.detail', {id: response.data.accounts[0]}, {reload: true});
                    } else if (response.data.contacts.length) {
                        // Contact found so redirect to the contact.
                        $state.go('base.contacts.detail', {id: response.data.contacts[0]}, {reload: true});
                    } else {
                        // No account or contact found so redirect to create account form.
                        $state.go(
                            'base.accounts.create',
                            {
                                'name': call.caller_name,
                                'phone_number': call.caller_number,
                            },
                            {reload: true}
                        );
                    }
                });
            } else {
                toastr.error('No calls for you right now', 'No calls');
            }
        });
    }
}
