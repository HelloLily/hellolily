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
        resolve: {
            teams: ['UserTeams', UserTeams => UserTeams.mine().$promise],
            dealStatuses: ['Deal', Deal => Deal.getStatuses().$promise],
        },
    });
}

angular.module('app.deals').controller('DealListController', DealListController);

DealListController.$inject = ['$filter', '$scope', '$state', '$timeout', 'Deal', 'HLFilters', 'HLUtils',
    'LocalStorage', 'Settings', 'Tenant', 'dealStatuses', 'teams'];
function DealListController($filter, $scope, $state, $timeout, Deal, HLFilters, HLUtils,
    LocalStorage, Settings, Tenant, dealStatuses, teams) {
    const vm = this;

    vm.storage = new LocalStorage('dealList');
    vm.storedFilterSpecialList = vm.storage.get('filterSpecialListSelected', null);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);

    Settings.page.setAllTitles('list', 'deals');

    /**
     * Table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filterQuery: '',
        archived: vm.storage.get('archived', false),
        order: vm.storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        visibility: vm.storage.get('visibility', {
            deal: true,
            client: true,
            status: true,
            created: true,
            name: true,
            amountOnce: true,
            amountRecurring: true,
            assignedTo: true,
            nextStep: true,
            nextStepDate: true,
            newBusiness: true,
            createdBy: true,
            tags: true,
            closedDate: false,
            lostReason: false,
        }),
        dueDateFilter: vm.storage.get('dueDateFilter', ''),
        usersFilter: vm.storage.get('usersFilter', ''),
        searchQuery: vm.storage.get('searchQuery', ''),
    };
    vm.displayFilterClear = false;
    vm.displaySpecialFilterClear = false;
    vm.filterList = [];
    vm.filterSpecialList = [];
    vm.showEmptyState = false;

    vm.updateDeals = updateDeals;
    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.updateModel = updateModel;
    vm.assignToMyTeams = assignToMyTeams;
    vm.removeFromList = removeFromList;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough
        $timeout(() => {
            _setupWatchers();
            _getFilterOnList();
            _getFilterSpecialList();
            showEmptyState();
        }, 150);

        Tenant.query({}, tenant => {
            vm.tenant = tenant;
        });

        vm.myTeams = teams;
    }

    function updateModel(data, field) {
        const deal = $filter('where')(vm.table.items, {id: data.id});

        return Deal.updateModel(data, field, deal).then(() => {
            updateDeals();
        });
    }

    /**
     * showEmptyState is used to count the total amount of deals used to show or not
     * show the empty state.
     */
    function showEmptyState() {
        // TODO: Use more db friendly check if empty state should be shown.
        // Deal.query({}, data => {
        //     if (data.pagination.total === 0) {
        //         vm.showEmptyState = true;
        //     }
        // });
    }

    function assignToMyTeams({id}) {
        const data = {
            id,
            assigned_to_teams: vm.myTeams.map(team => ({id: team.id})),
        };

        updateModel(data, 'assigned_to_teams');
    }

    function _getFilterOnList() {
        const filterList = [
            {
                name: 'New business',
                value: 'new_business:true',
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
        ];

        dealStatuses.results.forEach(status => {
            filterList.push({
                name: status.name,
                value: 'status.id:' + status.id,
                selected: false,
            });
        });

        // Merge previous stored selection with new filters.
        HLFilters.getStoredSelections(filterList, vm.storedFilterList);

        vm.filterList = filterList;

        // Watch doesn't get triggered here, so manually call _updateTableSettings.
        _updateTableSettings();
    }

    /**
     * Gets the deal next step filter list. Merges selections with locally stored values.
     *
     * @returns filterSpecialList (object): object containing the filter list.
     */
    function _getFilterSpecialList() {
        Deal.getNextSteps(response => {
            const filterList = [];

            angular.forEach(response.results, nextStep => {
                filterList.push({
                    name: nextStep.name,
                    value: 'next_step.id:' + nextStep.id,
                    selected: false,
                    position: nextStep.position,
                    isSpecialFilter: true,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterSpecialList);

            // Update filterList once AJAX calls are done.
            vm.filterSpecialList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage
     */
    function _updateTableSettings() {
        vm.storage.put('searchQuery', vm.table.searchQuery);
        vm.storage.put('archived', vm.table.archived);
        vm.storage.put('order', vm.table.order);
        vm.storage.put('visibility', vm.table.visibility);
        vm.storage.put('filterListSelected', vm.filterList);
        vm.storage.put('filterSpecialSelected', vm.filterSpecialList);
    }

    function updateDeals() {
        const blockTarget = '#tableBlockTarget';
        HLUtils.blockUI(blockTarget, true);

        Deal.getDeals(
            vm.table.order.column,
            vm.table.order.descending,
            vm.table.filterQuery,
            vm.table.searchQuery,
            vm.table.page,
            vm.table.pageSize
        ).then(data => {
            vm.table.items = data.objects;
            vm.table.totalItems = data.total;

            HLUtils.unblockUI(blockTarget);
        });
    }

    function removeFromList(deal) {
        const index = vm.table.items.indexOf(deal);
        vm.table.items.splice(index, 1);
        $scope.$apply();
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
        ], () => {
            _updateTableSettings();
            updateDeals();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', () => {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the values are retrieved from local storage,
         * the filterQuery changes and a new set of deals is fetched
         */
        $scope.$watch('vm.filterList', () => {
            updateFilterQuery();

            vm.selectedFilters = $filter('filter')(vm.filterList, {selected: true});
        }, true);

        $scope.$watchCollection('vm.filterSpecialList', () => {
            updateFilterQuery();
        });

        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], () => {
            updateFilterQuery();
            vm.storage.put('dueDateFilter', vm.table.dueDateFilter);
            vm.storage.put('usersFilter', vm.table.usersFilter);
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

    $scope.$on('$viewContentLoaded', () => {
        angular.element('.hl-search-field').focus();
    });
}
