angular.module('app.dashboard.directives').directive('unassignedDeals', unassignedDealsDirective);

function unassignedDealsDirective() {
    return {
        templateUrl: 'dashboard/directives/unassigneddeals.html',
        controller: UnassignedDealsController,
        controllerAs: 'vm',
        bindToController: true,
        scope: {
            team: '=',
        },
    };
}

UnassignedDealsController.$inject = ['$http', '$scope', '$state', 'Deal', 'HLFilters', 'HLUtils', 'LocalStorage'];
function UnassignedDealsController($http, $scope, $state, Deal, HLFilters, HLUtils, LocalStorage) {
    var vm = this;

    if (vm.team) {
        vm.storageName = 'unassignedDealsForTeam' + vm.team.id + 'Widget';
    } else {
        vm.storageName = 'unassignedDealsWidget';
    }

    vm.storage = new LocalStorage(vm.storageName);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);
    vm.highPrioDeals = 0;
    vm.table = {
        order: vm.storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };

    vm.assignToMe = assignToMe;
    vm.updateTable = updateTable;

    activate();

    /////

    function activate() {
        _watchTable();

        Deal.getNextSteps(function(response) {
            var filterList = [];

            angular.forEach(response.results, function(nextStep) {
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
        });
    }

    function updateTable() {
        var filterQuery = 'is_archived:false AND _missing_:assigned_to.id';
        var blockTarget = '#unassignedDealsBlockTarget';

        if (vm.team) {
            filterQuery += ' AND assigned_to_teams:' + vm.team.id;
            blockTarget += vm.team.id;
        } else {
            filterQuery += ' AND _missing_:assigned_to_teams';
        }

        HLUtils.blockUI(blockTarget, true);

        if (vm.table.filterQuery) {
            filterQuery += ' AND ' + vm.table.filterQuery;
        }

        Deal.getDeals(vm.table.order.column, vm.table.order.descending, filterQuery).then(function(data) {
            vm.table.items = data.objects;

            HLUtils.unblockUI(blockTarget);
        });
    }

    function assignToMe(dealObj) {
        swal({
            text: sprintf(messages.alerts.assignTo.questionText, {type: 'deal'}),
            type: 'question',
            showCancelButton: true,
        }).then(function(isConfirm) {
            if (isConfirm) {
                Deal.patch({id: dealObj.id, assigned_to: currentUser.id}).$promise.then(function() {
                    var index = vm.table.items.indexOf(dealObj);
                    vm.table.items.splice(index, 1);

                    $state.reload();
                });
            }
        }).done();
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            updateTable();
            vm.storage.put('order', vm.table.order);
        });
    }
}
