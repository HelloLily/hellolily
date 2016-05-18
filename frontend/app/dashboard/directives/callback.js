angular.module('app.dashboard.directives').directive('callbackRequests', CallbackRequestsDirective);

function CallbackRequestsDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/callback.html',
        controller: CallbackRequestsController,
        controllerAs: 'vm',
    };
}

CallbackRequestsController.$inject = ['$scope', 'Account', 'Case', 'Contact', 'HLUtils', 'LocalStorage'];
function CallbackRequestsController($scope, Account, Case, Contact, HLUtils, LocalStorage) {
    var vm = this;
    var storage = new LocalStorage('callbackWidget');

    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };

    activate();

    ///////////

    function activate() {
        _watchTable();
    }

    function _getCallbackRequests() {
        var filterQuery = 'archived:false AND casetype_name:Callback AND assigned_to_id:' + currentUser.id;

        HLUtils.blockUI('#callbackBlockTarget', true);

        Case.getCases(
            vm.table.order.column,
            vm.table.order.descending,
            filterQuery
        ).then(function(data) {
            angular.forEach(data.objects, function(callbackCase) {
                if (callbackCase.account) {
                    Account.get({id: callbackCase.account}, function(account) {
                        if (account.phone_numbers.length) {
                            callbackCase.accountPhone = account.phone_numbers[0].number;
                        }
                    });
                }

                if (callbackCase.contact) {
                    Contact.get({id: callbackCase.contact}, function(contact) {
                        if (contact.phone_numbers.length) {
                            callbackCase.contactPhone = contact.phone_numbers[0].number;
                        }
                    });
                }
            });

            vm.table.items = data.objects;

            HLUtils.unblockUI('#callbackBlockTarget');
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getCallbackRequests();
            storage.put('order', vm.table.order);
        });
    }
}
