angular.module('app.dashboard.directives').directive('myDeals', myDealsDirective);

function myDealsDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mydeals.html',
        controller: MyDealsController,
        controllerAs: 'vm',
    };
}

MyDealsController.$inject = ['$filter', '$scope', '$timeout', 'Case', 'Deal', 'HLUtils', 'HLResource', 'HLSockets', 'LocalStorage', 'Tenant'];
function MyDealsController($filter, $scope, $timeout, Case, Deal, HLUtils, HLResource, HLSockets, LocalStorage, Tenant) {
    const vm = this;
    const storage = new LocalStorage('deals');

    vm.highPrioDeals = 0;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'next_step.date_increment', // string: current sorted column
        }),
        items: [],
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
        conditions: {
            dueDate: false,
            user: false,
        },
    };
    vm.numOfDeals = 0;

    vm.getMyDeals = getMyDeals;
    vm.acceptDeal = acceptDeal;
    vm.updateModel = updateModel;

    HLSockets.bind('deal-assigned', getMyDeals);

    $scope.$on('$destroy', () => {
        HLSockets.unbind('deal-assigned', getMyDeals);
    });

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function getMyDeals(blockUI = false) {
        var field = 'next_step.position';
        var descending = false;
        var filterQuery = 'is_archived:false AND NOT next_step.name:"None"';

        if (blockUI) HLUtils.blockUI('#myDealsBlockTarget', true);

        if (vm.table.dueDateFilter) {
            filterQuery += ' AND ' + vm.table.dueDateFilter;
        }

        if (vm.table.usersFilter) {
            filterQuery += ' AND (' + vm.table.usersFilter + ')';
        }

        Deal.getDeals(field, descending, filterQuery).then(data => {
            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': data.objects,
                };
            } else {
                const accounts = [];

                data.objects.forEach(deal => {
                    const accountQuery = `account.id:${deal.account.id}`;

                    if (!accounts.includes(accountQuery)) {
                        accounts.push(accountQuery);
                    }
                });

                if (accounts.length) {
                    const filterquery = `(${accounts.join(' OR ')}) AND is_archived:false`;

                    Case.search({filterquery}).$promise.then(caseList => {
                        caseList.objects.forEach(accountCase => {
                            data.objects.forEach(deal => {
                                if (accountCase.account.id === deal.account.id) {
                                    deal.hasUnarchivedCases = true;
                                }
                            });
                        });

                        vm.table.items = HLUtils.timeCategorizeObjects(data.objects, 'next_step_date');
                    });
                } else {
                    vm.table.items = HLUtils.timeCategorizeObjects(data.objects, 'next_step_date');
                }
            }

            if (blockUI) HLUtils.unblockUI('#myDealsBlockTarget');

            vm.numOfDeals = data.objects.length;
        });

        Tenant.query({}, tenant => {
            vm.tenant = tenant;
        });
    }

    function updateModel(data, field) {
        const deal = $filter('where')(vm.table.items, {id: data.id});

        return Deal.updateModel(data, field, deal).then(response => {
            getMyDeals();
        });
    }

    function acceptDeal({id}) {
        const args = {
            id,
            newly_assigned: false,
        };

        updateModel(args);
    }

    function _watchTable() {
        $scope.$watch('vm.table.dueDateFilter', (newValue, oldValue) => {
            if (newValue || oldValue) {
                getMyDeals(true);
                storage.put('dueDateFilter', vm.table.dueDateFilter);
            }
        });

        $scope.$watch('vm.table.usersFilter', (newValue, oldValue) => {
            if (newValue || oldValue) {
                getMyDeals(true);
                storage.put('usersFilter', vm.table.usersFilter);
            }
        });
    }
}
