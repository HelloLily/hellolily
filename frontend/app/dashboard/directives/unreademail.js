angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmailDirective);

function unreadEmailDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/unreademail.html',
        controller: UnreadEmailController,
        controllerAs: 'vm',
    };
}

UnreadEmailController.$inject = ['$scope', '$interval', 'EmailAccount', 'EmailMessage', 'HLFilters', 'HLUtils', 'LocalStorage'];
function UnreadEmailController($scope, $interval, EmailAccount, EmailMessage, HLFilters, HLUtils, LocalStorage) {
    var vm = this;
    let reloadInterval;

    vm.storage = new LocalStorage('unreadEmailWidget');
    vm.storedFilterList = vm.storage.get('filterListSelected', null);
    vm.table = {
        order: vm.storage.get('order', {
            descending: true,
            column: 'sent_date',  // string: current sorted column
        }),
        items: [],
    };

    vm.updateTable = updateTable;

    reloadInterval = $interval(updateTable, 60000);

    $scope.$on('$destroy', function() {
        if (reloadInterval) {
            $interval.cancel(reloadInterval);
            reloadInterval = null;
        }
    });

    activate();

    //////

    function activate() {
        _watchTable();

        EmailAccount.mine(function(emailAccounts) {
            var filterList = [];

            angular.forEach(emailAccounts, function(account) {
                filterList.push({
                    id: 'account',
                    name: account.label,
                    value: account.id,
                    selected: false,
                    isSpecialFilter: true,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;
        });
    }

    function updateTable(blockUI = false) {
        var sort = HLUtils.getSorting(vm.table.order.column, vm.table.order.descending);

        if (blockUI) HLUtils.blockUI('#unreadEmailBlockTarget', true);

        const searchParams = {
            label: 'INBOX',
            sort: sort,
            read: 0,
        };
        if (vm.table.accountFilter) {
            searchParams.account = vm.table.accountFilter;
        }

        EmailMessage.search(searchParams, data => {
            vm.table.items = data.hits;

            if (blockUI) HLUtils.unblockUI('#unreadEmailBlockTarget');
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            updateTable(true);
            vm.storage.put('order', vm.table.order);
        });
    }
}
