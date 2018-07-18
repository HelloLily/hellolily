angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/controllers/list.html',
                controller: CaseListController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Cases',
        },
    });
}

angular.module('app.cases').controller('CaseListController', CaseListController);

CaseListController.$inject = ['$filter', '$scope', '$timeout', 'Case', 'HLFilters', 'HLUtils', 'LocalStorage',
    'Settings', 'UserTeams'];
function CaseListController($filter, $scope, $timeout, Case, HLFilters, HLUtils, LocalStorage, Settings, UserTeams) {
    const vm = this;

    vm.storage = new LocalStorage('cases');
    vm.storedFilterSpecialList = vm.storage.get('filterSpecialListSelected', null);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);

    Settings.page.setAllTitles('list', 'cases');

    /**
     * Table object: stores all the information to correctly display the table.
     */
    vm.table = {
        page: 1,  // Current page of pagination: 1-index.
        pageSize: 60,  // Number of items per page.
        totalItems: 0, // Total number of items.
        order: vm.storage.get('order', {
            descending: true,
            column: 'expires',  // String: current sorted column.
        }),
        visibility: vm.storage.get('visibility', {
            caseId: true,
            client: true,
            subject: true,
            priority: true,
            type: true,
            status: true,
            expires: true,
            created: true,
            assignedTo: true,
            createdBy: true,
            tags: true,
        }),
        dueDateFilter: vm.storage.get('dueDateFilter', ''),
        usersFilter: vm.storage.get('usersFilter', ''),
        searchQuery: vm.storage.get('searchQuery', ''),
    };
    vm.displayFilterClear = false;
    vm.displaySpecialFilterClear = false;
    vm.filterList = [];
    vm.filterSpecialList = [];
    vm.users = [];
    vm.showEmptyState = false;

    vm.updateCases = updateCases;
    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.updateModel = updateModel;
    vm.assignToMyTeams = assignToMyTeams;
    vm.removeFromList = removeFromList;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough.
        $timeout(() => {
            _getFilterSpecialList();
            _setupWatchers();
            showEmptyState();
        }, 50);
    }

    function updateModel(data, field) {
        let filtered = $filter('where')(vm.table.items, {id: data.id});

        if (filtered.length) {
            filtered = filtered[0];
        }

        return Case.updateModel(data, field, filtered).then(() => {
            updateCases();
        });
    }

    /**
     * setSearchQuery() sets the search query of the table.
     *
     * @param queryString string: string that will be set as the new search query on the table.
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    /**
     * showEmptyState is used to count the total amount of cases used to show or not
     * show the empty state.
     */
    function showEmptyState() {
        // TODO: Use more db friendly check if empty state should be shown.
        // Case.query({}, data => {
        //     if (data.pagination.total === 1) {
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

    /**
     * Gets the case type filter list. Merges selections with locally stored values.
     *
     * @returns filterSpecialList (object): object containing the filter list.
     */
    function _getFilterSpecialList() {
        Case.getCaseTypes({is_archived: 'All'}).$promise.then(caseTypes => {
            const filterList = [];

            // Get a list with all case types and add each one as a filter.
            caseTypes.results.forEach(caseType => {
                filterList.push({
                    name: caseType.name,
                    value: 'type.id:' + caseType.id,
                    selected: false,
                    isSpecialFilter: true,
                    isArchived: caseType.is_archived,
                });
            });

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, vm.storedFilterSpecialList);

            vm.filterSpecialList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage.
     */
    function _updateTableSettings() {
        vm.storage.put('searchQuery', vm.table.searchQuery);
        vm.storage.put('archived', vm.table.archived);
        vm.storage.put('order', vm.table.order);
        vm.storage.put('visibility', vm.table.visibility);
        vm.storage.put('filterListSelected', vm.filterList);
        vm.storage.put('filterSpecialSelected', vm.filterSpecialList);
    }

    function updateCases() {
        const blockTarget = '#tableBlockTarget';
        HLUtils.blockUI(blockTarget, true);

        Case.getCases(
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

    function removeFromList(caseObj) {
        const index = vm.table.items.indexOf(caseObj);
        vm.table.items.splice(index, 1);
        $scope.$apply();
    }

    function _setupWatchers() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of cases.
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
            updateCases();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache.
         */
        $scope.$watchCollection('vm.table.visibility', () => {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the stored values are loaded,
         * the filterQuery changes and a new set of cases is fetched.
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
