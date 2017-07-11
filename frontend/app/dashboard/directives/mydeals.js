angular.module('app.dashboard.directives').directive('myDeals', myDealsDirective);

function myDealsDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mydeals.html',
        controller: MyDealsController,
        controllerAs: 'vm',
    };
}

MyDealsController.$inject = ['$filter', '$scope', 'Case', 'Deal', 'HLUtils', 'HLResource', 'HLSockets', 'LocalStorage', 'Tenant'];
function MyDealsController($filter, $scope, Case, Deal, HLUtils, HLResource, HLSockets, LocalStorage, Tenant) {
    var storage = new LocalStorage('deals');

    var vm = this;
    vm.highPrioDeals = 0;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'next_step.date_increment', // string: current sorted column
        }),
        items: [],
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
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

        Deal.getDeals(field, descending, filterQuery).then(function(data) {
            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': data.objects,
                };
            } else {
                vm.table.items = HLUtils.timeCategorizeObjects(data.objects, 'next_step_date');

                angular.forEach(data.objects, function(deal) {
                    Case.search({filterquery: 'account.id:' + deal.account.id + ' AND is_archived:false'}).$promise.then(function(caseList) {
                        if (caseList.objects.length > 0) {
                            deal.hasUnarchivedCases = true;
                        }
                    });
                });
            }

            if (blockUI) HLUtils.unblockUI('#myDealsBlockTarget');

            vm.numOfDeals = data.objects.length;
        });

        Tenant.query({}, function(tenant) {
            vm.tenant = tenant;
        });
    }

    function updateModel(data, field) {
        var deal = $filter('where')(vm.table.items, {id: data.id});

        return Deal.updateModel(data, field, deal).then(function(response) {
            getMyDeals();
        });
    }

    function acceptDeal(myDeal) {
        var args = {
            id: myDeal.id,
            newly_assigned: false,
        };

        updateModel(args);
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            getMyDeals(true);
            storage.put('order', vm.table.order);
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }
}
