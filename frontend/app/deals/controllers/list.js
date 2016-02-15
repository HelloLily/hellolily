angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals', {
        url: '/deals',
        views: {
            '@': {
                templateUrl: 'deals/controllers/list.html',
                controller: DealListController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Deals',
        },
    });
}

angular.module('app.deals').controller('DealListController', DealListController);

DealListController.$inject = ['$scope', '$timeout', 'Settings', 'LocalStorage', 'Deal', 'HLFilters'];
function DealListController($scope, $timeout, Settings, LocalStorage, Deal, HLFilters) {
    var storage = LocalStorage('deals');
    var vm = this;

    Settings.page.setAllTitles('list', 'deals');

    /**
     * table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filterQuery: '',
        archived: storage.get('archived', false),
        order: storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        visibility: storage.get('visibility', {
            deal: true,
            client: true,
            stage: true,
            created: true,
            name: true,
            amountOnce: true,
            amountRecurring: true,
            assignedTo: true,
            nextStep: true,
            nextStepDate: true,
            feedbackFormSent: true,
            newBusiness: true,
            tags: true,
        }),
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
        searchQuery: storage.get('searchQuery', ''),
    };
    vm.displayFilterClear = false;
    vm.displaySpecialFilterClear = false;
    vm.filterList = [];

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough
        $timeout(function() {
            _setupWatchers();
            _getFilterList();
        }, 50);
    }

    function _getFilterList() {
        var storedFilterList = storage.get('filterListSelected', null);
        var filterList;

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (storedFilterList) {
            vm.filterList = storedFilterList;
        }

        // But we still update the list afterwards (in case a filter was changed)
        filterList = [
            {
                name: 'Assigned to me',
                value: 'assigned_to_id:' + currentUser.id,
                selected: false,
            },
            {
                name: 'New business',
                value: 'new_business:true',
                selected: false,
            },
            {
                name: 'Proposal stage',
                value: 'stage:1',
                selected: false,
            },
            {
                name: 'Won stage',
                value: 'stage:2',
                selected: false,
            },
            {
                name: 'Called',
                value: 'stage:4',
                selected: false,
            },
            {
                name: 'Emailed',
                value: 'stage:5',
                selected: false,
            },
            {
                name: 'Feedback form not sent',
                value: 'feedback_form_sent:false',
                selected: false,
            },
            {
                name: 'Age between 7 and 30 days',
                value: 'created:[' + moment().subtract(30, 'd').format('YYYY-MM-DD') + ' TO ' + moment().subtract(7, 'd').format('YYYY-MM-DD') + ']',
                selected: false,
            },
            {
                name: 'Age between 30 and 120 days',
                value: 'created:[' + moment().subtract(120, 'd').format('YYYY-MM-DD') + ' TO ' + moment().subtract(30, 'd').format('YYYY-MM-DD') + ']',
                selected: false,
            },
            {
                name: 'Archived',
                value: '',
                selected: false,
                id: 'archived',
            },
        ];

        Deal.getNextSteps(function(nextSteps) {
            angular.forEach(nextSteps, function(nextStep) {
                filterList.push({
                    name: nextStep.name,
                    value: 'next_step.id:' + nextStep.id,
                    selected: false,
                    isSpecialFilter: true,
                    position: nextStep.position,
                });
            });

            HLFilters.getStoredSelections(filterList, storedFilterList);

            // Update filterList once AJAX calls are done.
            vm.filterList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage
     */
    function _updateTableSettings() {
        storage.put('searchQuery', vm.table.searchQuery);
        storage.put('archived', vm.table.archived);
        storage.put('order', vm.table.order);
        storage.put('visibility', vm.table.visibility);
        storage.put('filterListSelected', vm.filterList);
    }

    /**
     * _updateDeals() reloads the deals through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateDeals() {
        Deal.getDeals(
            vm.table.searchQuery,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.descending,
            vm.table.filterQuery
        ).then(function(deals) {
            vm.table.items = deals;
            vm.table.totalItems = deals.length ? deals[0].total_size : 0;
        });
    }

    function _setupWatchers() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of deals
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.descending',
            'vm.table.searchQuery',
            'vm.table.archived',
            'vm.table.filterQuery',
        ], function() {
            _updateTableSettings();
            _updateDeals();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the values are retrieved from local storage,
         * the filterQuery changes and a new set of deals is fetched
         */
        $scope.$watchCollection('vm.filterList', function() {
            updateFilterQuery();
        });

        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            updateFilterQuery();
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm, true);
    }

    function clearFilters(clearSpecial) {
        HLFilters.clearFilters(vm, clearSpecial);
    }
}
