angular.module('app.dashboard.directives').directive('myDeals', myDealsDirective);

function myDealsDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mydeals.html',
        controller: MyDealsController,
        controllerAs: 'vm',
    };
}

MyDealsController.$inject = ['$scope', 'Deal', 'HLUtils', 'LocalStorage', 'CaseDetail'];
function MyDealsController($scope, Deal, HLUtils, LocalStorage, CaseDetail) {
    var storage = LocalStorage('myDealsWidget');

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

    vm.openPostponeWidget = openPostponeWidget;
    vm.getMyDeals = getMyDeals;
    vm.numOfDeals = 0;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function getMyDeals() {
        var field = 'next_step.position';
        var descending = false;

        var filterQuery = 'archived:false AND NOT next_step.name:"None"';

        if (vm.table.dueDateFilter) {
            filterQuery += ' AND ' + vm.table.dueDateFilter;
        } else {
            // Only display deals with a next step date.
            filterQuery += ' AND next_step_date:*';
        }

        if (vm.table.usersFilter) {
            filterQuery += ' AND (' + vm.table.usersFilter + ')';
        } else {
            filterQuery += ' AND assigned_to_id:' + currentUser.id;
        }

        var dealPromise = Deal.getDeals('', 1, 250, field, descending, filterQuery);
        dealPromise.then(function(data) {
            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': data,
                };
            } else {
                vm.table.items = HLUtils.timeCategorizeObjects(data, 'next_step_date');

                angular.forEach(data, function(deal) {
                    CaseDetail.query({filterquery: 'account:' + deal.account + ' AND archived:false'}).$promise.then(function(caseList) {
                        if (caseList.length > 0) {
                            deal.hasUnarchivedCases = true;
                        }
                    });
                });
            }

            vm.numOfDeals = data.length;
        });
    }

    function openPostponeWidget(deal) {
        var modalInstance = Deal.openPostponeWidget(deal, true);

        modalInstance.result.then(function() {
            getMyDeals();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            getMyDeals();
            storage.put('order', vm.table.order);
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }
}
