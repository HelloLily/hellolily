angular.module('app.dashboard.directives').directive('unassignedDeals', unassignedDealsDirective);

function unassignedDealsDirective() {
    return {
        templateUrl: 'dashboard/directives/unassigneddeals.html',
        controller: UnassignedDealsController,
        controllerAs: 'vm',
        bindToController: true,
        scope: {
            teams: '=',
        },
    };
}

UnassignedDealsController.$inject = ['$http', '$scope', '$state', '$timeout', 'Deal', 'HLFilters', 'HLUtils', 'HLSockets', 'LocalStorage'];
function UnassignedDealsController($http, $scope, $state, $timeout, Deal, HLFilters, HLUtils, HLSockets, LocalStorage) {
    const vm = this;

    vm.storageName = 'unassignedDealsWidget';
    vm.storage = new LocalStorage(vm.storageName);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);
    vm.storedFilterSpecialList = vm.storage.get('filterSpecialListSelected', null);
    vm.highPrioDeals = 0;
    vm.table = {
        order: vm.storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };
    vm.filterList = [];
    vm.filterSpecialList = [];

    vm.assignToMe = assignToMe;
    vm.updateTable = updateTable;

    HLSockets.bind('deal-unassigned', updateTable);

    $scope.$on('$destroy', () => {
        HLSockets.unbind('deal-unassigned', updateTable);
    });

    $timeout(activate);

    /////

    function activate() {
        let filterSpecialList = [{
            name: 'Unassigned',
            value: '_missing_:assigned_to_teams',
            selected: false,
            isSpecialFilter: true,
            separate: true,
        }];

        vm.teams.map((team) => {
            filterSpecialList.unshift({
                name: team.name,
                value: 'assigned_to_teams:' + team.id,
                selected: team.selected,
                isSpecialFilter: true,
                separate: true,
            });
        });

        HLFilters.getStoredSelections(filterSpecialList, vm.storedFilterSpecialList);

        vm.filterSpecialList = filterSpecialList;

        Deal.getNextSteps((response) => {
            let filterList = [];

            angular.forEach(response.results, (nextStep) => {
                filterList.push({
                    name: nextStep.name,
                    value: 'next_step.id:' + nextStep.id,
                    selected: false,
                    position: nextStep.position,
                    isSpecialFilter: true,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;

            _watchTable();
        });
    }

    function updateTable(blockUI = false) {
        const blockTarget = '#unassignedDealsBlockTarget';
        let filterQuery = 'is_archived:false AND _missing_:assigned_to.id';

        if (blockUI) HLUtils.blockUI(blockTarget, true);

        if (vm.table.filterQuery) {
            filterQuery += ' AND ' + vm.table.filterQuery;
        }

        Deal.getDeals(vm.table.order.column, vm.table.order.descending, filterQuery).then(data => {
            vm.table.items = data.objects;

            if (blockUI) HLUtils.unblockUI(blockTarget);
        });
    }

    function assignToMe(dealObj) {
        swal({
            text: sprintf(messages.alerts.assignTo.questionText, {type: 'deal'}),
            type: 'question',
            showCancelButton: true,
        }).then(isConfirm => {
            if (isConfirm) {
                Deal.patch({id: dealObj.id, assigned_to: currentUser.id}).$promise.then(() => {
                    const index = vm.table.items.indexOf(dealObj);
                    vm.table.items.splice(index, 1);

                    $state.reload();
                });
            }
        }).done();
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], (newValue, oldValue) => {
            if (newValue !== oldValue) {
                updateTable(true);
                vm.storage.put('order', vm.table.order);
            }
        });
    }
}
