/**
 * caseControllers is a container for all case related Controllers
 */
var caseControllers = angular.module('CaseControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'AccountServices',
    'CaseServices',
    'contactServices',
    'noteServices',
    'app.email.services'
]);

caseControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/list.html',
                controller: 'CaseListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Cases'
        }
    });
    $stateProvider.state('base.cases.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'cases/detail.html',
                controller: 'CaseDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ case.subject }}'
        }
    });
    $stateProvider.state('base.cases.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/update/' + elem.id +'/';
                },
                controller: 'CaseEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
    $stateProvider.state('base.cases.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'CaseDeleteController'
            }
        },
    });
    $stateProvider.state('base.cases.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/cases/create',
                controller: 'CaseCreateController'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.cases.create.fromContact', {
        url: '/contact/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_contact/' + elem.id +'/';
                },
                controller: 'CaseCreateController'
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
    $stateProvider.state('base.cases.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_account/' + elem.id +'/';
                },
                controller: 'CaseCreateController'
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}]);

/**
 * CaseDetailController is a controller to show details of a case.
 */
caseControllers.controller('CaseDetailController', [
    '$filter',
    '$http',
    '$location',
    '$q',
    '$scope',
    '$state',
    '$stateParams',

    'CaseDetail',
    'CaseStatuses',
    'NoteDetail',
    'NoteService',

    function($filter, $http, $location, $q, $scope, $state, $stateParams, CaseDetail, CaseStatuses, NoteDetail, NoteService) {
        $scope.conf.pageTitleBig = 'Case';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';

        var id = $stateParams.id;

        $scope.case = CaseDetail.get({id: id});
        $scope.caseStatuses = CaseStatuses.query();

        /**
         *
         * @returns {string}: A string which states what label should be displayed
         */
        $scope.getPriorityDisplay = function () {
            if ($scope.case.is_archived) {
                return 'label-default';
            } else {
                switch ($scope.case.priority) {
                    case 0:
                        return 'label-success';
                    case 1:
                        return 'label-info';
                    case 2:
                        return 'label-warning';
                    case 3:
                        return 'label-danger';
                    default :
                        return 'label-info';
                }
            }
        };

        $scope.changeCaseStatus = function (status) {
            // TODO: LILY-XXX: Temporary call to change status of a case, will be replaced with an new API call later
            var req = {
                method: 'POST',
                url: '/cases/update/status/' + $scope.case.id + '/',
                data: 'status=' + status,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.case.status = data.status;
                }).
                error(function(data, status, headers, config) {
                    // Request failed proper error?
                });
        };

        $scope.assignCase = function () {
            var assignee = '';

            if ($scope.case.assigned_to_id != $scope.currentUser.id) {
                assignee = $scope.currentUser.id;
            }

            var req = {
                method: 'POST',
                url: '/cases/update/assigned_to/' + $scope.case.id + '/',
                data: 'assignee=' + assignee,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    if (data.assignee) {
                        $scope.case.assigned_to_id = data.assignee.id;
                        $scope.case.assigned_to_name = data.assignee.name;
                    }
                    else {
                        $scope.case.assigned_to_id = null;
                        $scope.case.assigned_to_name = null;
                    }
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };

        $scope.showMoreText = 'Show more';
        $scope.opts = {history_type: 'note'};
        $scope.history_types = [
            {type: 'note', name: 'Notes'}
        ];

        var add = 10,
            size = add,
            currentSize = 0;

        $scope.history = [];

        /**
         * Load history of notes for this deal for historylist.
         */
        function loadHistory() {
            var history = [];
            var notesPromise = NoteDetail.query({
                filterquery: 'content_type:case AND object_id:' + id,
                size: size
            }).$promise;

            $q.all([notesPromise]).then(function(results) {
                var notes = results[0];
                notes.forEach(function(note) {
                    note.history_type = 'note';
                    note.color = 'yellow';
                    history.push(note);
                });

                $scope.history.splice(0, $scope.history.length);
                $filter('orderBy')(history, 'date', true).forEach(function(item) {
                    $scope.history.push(item);
                });
                $scope.limitSize = size;
                size += add;
                if ($scope.history.length == 0) {
                    $scope.showMoreText = 'No history (refresh)';
                }
                else if ($scope.history.length <= currentSize || $scope.history.length < size / 4) {
                    $scope.showMoreText = 'End reached (refresh)';
                }
                currentSize = $scope.history.length;
            });
        }

        /**
         * Allows the (re)load of the history.
         */
        $scope.loadHistoryFromButton = function() {
            loadHistory();
        };

        $scope.loadHistoryFromButton();

        /**
         * Archive a deal.
         * TODO: LILY-XXX: Change to API based archiving
         */
        $scope.archive = function(id) {
            var req = {
                method: 'POST',
                url: '/cases/archive/',
                data: 'id=' + id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.case.archived = true;
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };

        /**
         * Unarchive a deal.
         * TODO: LILY-XXX: Change to API based unarchiving
         */
        $scope.unarchive = function(id) {
            var req = {
                method: 'POST',
                url: '/cases/unarchive/',
                data: 'id=' + id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.case.archived = false;
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };

        $scope.deleteNote = function(note) {
            if (confirm('Are you sure?')) {
                NoteService.delete({
                    id:note.id
                }, function() {  // On success
                    var index = $scope.history.indexOf(note);
                    $scope.history.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                });
            }
        };
    }
]);

/**
 * CaseListController is a controller to show list of cases
 *
 */
caseControllers.controller('CaseListController', [
    '$cookieStore',
    '$http',
    '$location',
    '$scope',
    '$window',

    'Case',
    'Cookie',
    'HLDate',
    'HLFilters',
    function ($cookieStore, $http, $location, $scope, $window, Case, Cookie, HLDate, HLFilters) {
        Cookie.prefix = 'caseList';

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
            searchQuery = Cookie.getCookieValue('searchQuery', '');
        }

        /**
         * table object: stores all the information to correctly display the table
         */
        $scope.table = {
            page: 1,  // current page of pagination: 1-index
            pageSize: 60,  // number of items per page
            totalItems: 0, // total number of items
            searchQuery: searchQuery,  // search query
            archived: Cookie.getCookieValue('archived', false),
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'expires'  // string: current sorted column
            }),
            visibility: Cookie.getCookieValue('visibility', {
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
            var filterListCookie = Cookie.getCookieValue('filterList', null);

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
            Cookie.setCookieValue('searchQuery', $scope.table.searchQuery);
            Cookie.setCookieValue('archived', $scope.table.archived);
            Cookie.setCookieValue('order', $scope.table.order);
            Cookie.setCookieValue('visibility', $scope.table.visibility);
            Cookie.setCookieValue('filterList', $scope.filterList);
        }

        /**
         * updateCases() reloads the cases through a service
         *
         * Updates table.items and table.totalItems
         */
        function updateCases() {
            Case.query(
                $scope.table
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

            if(confirm("Are you sure you want to delete case " + subject + "?")){
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
    }
]);

/**
 * Controller to create a case
 */
caseControllers.controller('CaseCreateController', [
    '$scope',

    function($scope) {
        $scope.conf.pageTitleBig = 'New case';
        $scope.conf.pageTitleSmall = 'making cases';
        HLCases.addAssignToMeButton();
        HLSelect2.init();
    }
]);

/**
 * Controller to edit a case
 */
caseControllers.controller('CaseEditController', [
    '$scope',
    '$stateParams',

    'CaseDetail',

    function($scope, $stateParams, CaseDetail) {
        var id = $stateParams.id;
        var casePromise = CaseDetail.get({id: id}).$promise;

        casePromise.then(function(caseObject) {
            $scope.case = caseObject;
            $scope.conf.pageTitleBig = caseObject.subject;
            $scope.conf.pageTitleSmall = 'change is natural';
            HLSelect2.init();
        });
    }
]);

/**
 * Controller to delete a case
 */
caseControllers.controller('CaseDeleteController', [
    '$http',
    '$state',
    '$stateParams',

    function($http, $state, $stateParams) {
        var id = $stateParams.id;

        var req = {
            method: 'POST',
            url: '/cases/delete/' + id + '/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $state.go('base.cases');
            }).
            error(function(data, status, headers, config) {
                $state.go('base.cases');
            });
    }
]);
