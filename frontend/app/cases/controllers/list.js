angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/controllers/list.html',
                controller: CaseListController
            }
        },
        ncyBreadcrumb: {
            label: 'Cases'
        }
    });
}

angular.module('app.cases').controller('CaseListController', CaseListController);

CaseListController.$inject = ['$http', '$location', '$modal', '$scope', '$state', 'Case', 'Cookie', 'HLDate', 'HLFilters'];
function CaseListController ($http, $location, $modal, $scope, $state, Case, Cookie, HLDate, HLFilters) {
    var cookie = Cookie('caseList');

    $scope.conf.pageTitleBig = 'Cases';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    // Setup search query
    var searchQuery = '';

    // Check if filter is set as query parameter
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
        pageSize: 60,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: searchQuery,  // search query
        archived: cookie.get('archived', false),
        order: cookie.get('order', {
            ascending: true,
            column: 'expires'  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            caseId: true,
            client: true,
            subject: true,
            priority: true,
            type: true,
            status: true,
            expires: true,
            assignedTo: true,
            createdBy: true,
            tags: true
        })
    };

    $scope.displayFilterClear = false;

    getFilterList();

    /**
     * Gets the filter list. Is either the value in the cookie or a new list
     *
     * @returns filterList (object): object containing the filter list
     */
    function getFilterList() {
        var filterListCookie = cookie.get('filterList', null);

        if (!filterListCookie) {
            var filterList = [
                {
                    name: 'Assigned to me',
                    value: 'assigned_to_id:' + $scope.currentUser.id,
                    selected: false
                },
                {
                    name: 'Assigned to nobody',
                    value: 'NOT(assigned_to_id:*)',
                    selected: false
                },
                {
                    name: 'Expired 7 days or more ago',
                    value: 'expires:[* TO ' + HLDate.getSubtractedDate(7) + ']',
                    selected: false
                },
                {
                    name: 'Expired 30 days or more ago',
                    value: 'expires:[* TO ' + HLDate.getSubtractedDate(30) + ']',
                    selected: false
                },
                {
                    name: 'Archived',
                    value: '',
                    selected: false,
                    id: 'archived'
                }
            ];

            // Update filterList for now
            $scope.filterList = filterList;

            Case.getCaseTypes().then(function (cases) {
                for (var key in cases) {
                    if (cases.hasOwnProperty(key)) {
                        filterList.push({
                            name: 'Case type ' + cases[key],
                            value: 'casetype_id:' + key,
                            selected: false
                        });
                    }
                }

                // Update filterList once AJAX call is done
                $scope.filterList = filterList;
                // Watch doesn't get triggered here, so manually call updateTableSettings
                updateTableSettings();
            });
        } else {
            // Cookie is set, so use it as the filterList
            $scope.filterList = filterListCookie;
        }
    }

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
     * updateCases() reloads the cases through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateCases() {
        Case.getCases(
            $scope.table.searchQuery,
            $scope.table.page,
            $scope.table.pageSize,
            $scope.table.order.column,
            $scope.table.order.ascending,
            $scope.table.archived,
            $scope.table.filterQuery
        ).then(function (data) {
                $scope.table.items = data.cases;
                $scope.table.totalItems = data.total;
            }
        );
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of cases
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.ascending',
        'table.searchQuery',
        'table.archived',
        'table.filterQuery'
    ], function () {
        updateTableSettings();
        updateCases();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', function () {
        updateTableSettings();
    });

    /**
     * Watches the filters so when the cookie is loaded,
     * the filterQuery changes and a new set of deals is fetched
     */
    $scope.$watchCollection('filterList', function () {
        $scope.updateFilterQuery();
    });

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    $scope.setSearchQuery = function (queryString) {
        $scope.table.searchQuery = queryString;
    };

    $scope.toggleArchived = function () {
        $scope.table.archived = !$scope.table.archived;
    };

    $scope.updateFilterQuery = function () {
        HLFilters.updateFilterQuery($scope);
    };

    $scope.clearFilters = function () {
        HLFilters.clearFilters($scope);
    };

    /**
     * Deletes the case in django and updates the angular view
     */
    $scope.delete = function(id, subject, cases) {
        var req = {
            method: 'POST',
            url: '/cases/delete/' + id + '/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        if(confirm('Are you sure you want to delete case ' + subject + '?')){
            $http(req).
                success(function(data, status, headers, config) {
                    var index = $scope.table.items.indexOf(cases);
                    $scope.table.items.splice(index, 1);
                }).
                error(function(data, status, headers, config) {
                    // Request failed proper error?
                });
        }
    };

    $scope.assignTo = function(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/assignto.html',
            controller: 'CaseAssignModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase;
                }
            }
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    };
}
