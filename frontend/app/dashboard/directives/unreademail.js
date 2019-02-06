angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmailDirective);

function unreadEmailDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/unreademail.html',
        controller: UnreadEmailController,
        controllerAs: 'vm',
    };
}

UnreadEmailController.$inject = ['$scope', '$timeout', '$interval', 'EmailAccount', 'EmailMessage', 'HLFilters', 'HLUtils', 'LocalStorage'];
function UnreadEmailController($scope, $timeout, $interval, EmailAccount, EmailMessage, HLFilters, HLUtils, LocalStorage) {
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

    $timeout(activate);

    //////

    function activate() {
        EmailAccount.mine(function(emailAccounts) {
            var filterList = [];

            angular.forEach(emailAccounts.results, function(account) {
                filterList.push({
                    name: account.label,
                    value: 'account.id:' +  account.id,
                    selected: false,
                    isSpecialFilter: true,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;
        });

        $timeout(_watchTable);
    }

    function updateTable(blockUI = false) {
        var sort = HLUtils.getSorting(vm.table.order.column, vm.table.order.descending);
        var filterQuery = 'read:false AND label_id:INBOX';

        if (blockUI) HLUtils.blockUI('#unreadEmailBlockTarget', true);

        if (vm.table.filterQuery) {
            filterQuery += ' AND ' + vm.table.filterQuery;
        }

        EmailMessage.search({
            filterquery: filterQuery,
            sort: sort,
        }, function(data) {
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
