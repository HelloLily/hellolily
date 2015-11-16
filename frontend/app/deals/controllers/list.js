angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals', {
        url: '/deals',
        views: {
            '@': {
                templateUrl: 'deals/controllers/list.html',
                controller: DealListController
            },
        },
        ncyBreadcrumb: {
            label: 'Deals',
        },
    });
}

angular.module('app.deals').controller('DealListController', DealListController);

DealListController.$inject = ['$location', '$scope', 'Settings', 'Cookie', 'Deal', 'HLFilters'];
function DealListController($location, $scope, Settings, Cookie, Deal, HLFilters) {
    var cookie = Cookie('dealList');

    Settings.page.setAllTitles('list', 'deals');

    // Setup search query
    var searchQuery = '';

    // Check if searchQuery is set as query parameter
    var search = $location.search().search;
    if (search != undefined) {
        searchQuery = search;
    } else {
        // Get searchQuery from cookie
        searchQuery = cookie.get('searchQuery', '');
    }

    /**
     * table object: stores all the information to correctly display the table
     */
    $scope.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: searchQuery,  // search query
        filterQuery: '',
        archived: cookie.get('archived', false),
        order: cookie.get('order', {
            ascending: true,
            column: 'closing_date',  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            deal: true,
            stage: true,
            created: true,
            name: true,
            amountOnce: true,
            amountRecurring: true,
            assignedTo: true,
            closingDate: true,
            feedbackFormSent: true,
            newBusiness: true,
            tags: true
        })};

    /**
     * stores the selected filters
     */
    $scope.filterList = cookie.get('filterList', [
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
    ]);

    /**
     * updateTableSettings() sets scope variables to the cookie
     */
    function updateTableSettings() {
        cookie.put('searchQuery', $scope.table.searchQuery);
        cookie.put('archived', $scope.table.archived);
        cookie.put('order', $scope.table.order);
        cookie.put('visibility', $scope.table.visibility);
        cookie.put('filterList', $scope.filterList);
    }

    /**
     * updateDeals() reloads the deals through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateDeals() {
        Deal.getDeals(
            $scope.table.searchQuery,
            $scope.table.page,
            $scope.table.pageSize,
            $scope.table.order.column,
            $scope.table.order.ascending,
            $scope.table.filterQuery
        ).then(function(deals) {
            $scope.table.items = deals;
            $scope.table.totalItems = deals.length ? deals[0].total_size : 0;
        });
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of deals
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.ascending',
        'table.searchQuery',
        'table.archived',
        'table.filterQuery',
    ], function() {
        updateTableSettings();
        updateDeals();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', function() {
        updateTableSettings();
    });

    /**
     * Watches the filters so when the cookie is loaded,
     * the filterQuery changes and a new set of deals is fetched
     */
    $scope.$watchCollection('filterList', function() {
        $scope.updateFilterQuery();
    });

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    $scope.setSearchQuery = function(queryString) {
        $scope.table.searchQuery = queryString;
    };

    $scope.toggleArchived = function() {
        $scope.table.archived = !$scope.table.archived;
    };

    $scope.updateFilterQuery = function() {
        HLFilters.updateFilterQuery($scope);
    };

    $scope.clearFilters = function() {
        HLFilters.clearFilters($scope);
    };
}
