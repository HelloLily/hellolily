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
        ga('send', 'event', 'Caller info', 'Open', 'Topnav');

        // Get the latest call of the current user based on the internal number.
        Call.getLatestCall().$promise.then(function(callInfo) {
            var call = callInfo.call;

            if (call) {
                // There was a call for the current user, so try to find an account with the given number.
                Account.searchByPhoneNumber({number: call.caller_number}).$promise.then(function(response) {
                    if (response.data) {
                        // Account found so redirect to the account.
                        $state.go('base.accounts.detail', {id: response.data.id}, {reload: true});
                    }
                });
            } else {
                toastr.error('No calls for you right now', 'No calls');
            }
        });
    }
}
