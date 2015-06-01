/**
 * dealsControllers is a container for all deals related Controllers
 */
var dealControllers = angular.module('DealControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',
    'ui.select',

    // Lily dependencies
    'app.deals.services'
]);

dealControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.deals', {
        url: '/deals',
        views: {
            '@': {
                templateUrl: 'deals/list.html',
                controller: 'DealListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Deals'
        }
    });
    $stateProvider.state('base.deals.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/detail.html',
                controller: 'DealDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ deal.name }}'
        }
    });
    $stateProvider.state('base.deals.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/deals/update/' + elem.id +'/';
                },
                controller: 'DealEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
    $stateProvider.state('base.deals.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'DealDeleteController'
            }
        },
    });
    $stateProvider.state('base.deals.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/deals/create',
                controller: 'DealCreateController'
            }
        },
        ncyBreadcrumb: {
            label: 'New'
        }
    });
    $stateProvider.state('base.deals.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/deals/create/from_account/' + elem.id +'/';
                },
                controller: 'DealCreateController'
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}]);

/**
 * DealListController controller to show list of deals
 */
dealControllers.controller('DealListController', [
    '$cookieStore',
    '$http',
    '$location',
    '$scope',
    '$window',

    'Cookie',
    'Deal',
    'HLDate',
    'HLFilters',
    function($cookieStore, $http, $location, $scope, $window, Cookie, Deal, HLDate, HLFilters) {
        var cookie = Cookie('dealList');

        $scope.conf.pageTitleBig = 'Deals';
        $scope.conf.pageTitleSmall = 'do all your lookin\' here';

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
            order:  cookie.get('order', {
                ascending: true,
                column:  'closing_date'  // string: current sorted column
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
                selected: false
            },
            {
                name: 'New business',
                value: 'new_business:true',
                selected: false
            },
            {
                name: 'Proposal stage',
                value: 'stage:1',
                selected: false
            },
            {
                name: 'Won stage',
                value: 'stage:2',
                selected: false
            },
            {
                name: 'Called',
                value: 'stage:4',
                selected: false
            },
            {
                name: 'Emailed',
                value: 'stage:5',
                selected: false
            },
            {
                name: 'Feedback form not sent',
                value: 'feedback_form_sent:false',
                selected: false
            },
            {
                name: 'Age between 7 and 30 days',
                value: 'created:[' + HLDate.getSubtractedDate(30) + ' TO ' + HLDate.getSubtractedDate(7) + ']',
                selected: false
            },
            {
                name: 'Age between 30 and 120 days',
                value: 'created:[' + HLDate.getSubtractedDate(120) + ' TO ' + HLDate.getSubtractedDate(30) + ']',
                selected: false
            },
            {
                name: 'Archived',
                value: '',
                selected: false,
                id: 'archived'
            }
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
                $scope.table.totalItems = deals.length ? deals[0].total_size: 0;
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
            'table.filterQuery'
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

        /**
         * Deletes the deal in django and updates the angular view
         */
        $scope.delete = function(id, name, deal) {
            var req = {
                method: 'POST',
                url: '/deals/delete/' + id + '/',
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            if(confirm("Are you sure you want to delete deal " + name + "?")){
                $http(req).
                    success(function(data, status, headers, config) {
                        var index = $scope.table.items.indexOf(deal);
                        $scope.table.items.splice(index, 1);
                    }).
                    error(function(data, status, headers, config) {
                        // Request failed propper error?
                    });
            }
        };
    }
]);

/**
 * This controller holds all the functions needed on the detail
 * page of a deal. It includes: Stage change, (un)archive, Delete
 */
dealControllers.controller('DealDetailController', [
    '$filter',
    '$http',
    '$location',
    '$scope',
    '$state',
    '$stateParams',
    '$q',

    'DealDetail',
    'DealStages',
    'NoteDetail',
    'NoteService',

    function($filter, $http, $location, $scope, $state, $stateParams, $q, DealDetail, DealStages, NoteDetails, NoteService) {
        $scope.conf.pageTitleBig = 'Deal detail';
        $scope.conf.pageTitleSmall = 'the devil is in the details';

        var id = $stateParams.id;

        $scope.deal = DealDetail.get({id: id});
        $scope.dealStages = DealStages.query();

        /**
         * Change the state of a deal
         */
        $scope.changeState = function(stage) {
            var newStage = stage;

            var req = {
                method: 'POST',
                url: '/deals/update/stage/' + $scope.deal.id + '/',
                data: 'stage=' + stage,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.deal.stage = newStage;
                    $scope.deal.stage_name = data.stage;
                    if(data.closed_date !== undefined){
                        $scope.deal.closing_date = data.closed_date;
                    }
                    $scope.loadNotifications();
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };

        /**
         * Archive a deal
         */
        $scope.archive = function(id) {
            var req = {
                method: 'POST',
                url: '/deals/archive/',
                data: 'id=' + id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.deal.archived = true;
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };

        /**
         * Unarchive a deal
         */
        $scope.unarchive = function(id) {
            var req = {
                method: 'POST',
                url: '/deals/unarchive/',
                data: 'id=' + id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            };

            $http(req).
                success(function(data, status, headers, config) {
                    $scope.deal.archived = false;
                }).
                error(function(data, status, headers, config) {
                    // Request failed propper error?
                });
        };
    }
]);

/**
 * Controller for editing a deal
 */
dealControllers.controller('DealEditController', [
    '$scope',
    '$stateParams',

    'DealDetail',

    function($scope, $stateParams, DealDetail) {
        var id = $stateParams.id;
        var dealPromise = DealDetail.get({id: id}).$promise;

        dealPromise.then(function(deal) {
            $scope.deal = deal;
            $scope.conf.pageTitleBig = 'Edit ' + deal.name;
            $scope.conf.pageTitleSmall = 'change is natural';
        });
    }
]);

/**
 * Controller for deleting a deal
 */
dealControllers.controller('DealDeleteController', [
    '$http',
    '$state',
    '$stateParams',

    function($http, $state, $stateParams) {
        var id = $stateParams.id;
        var req = {
            method: 'POST',
            url: '/deals/delete/' + id + '/',
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                $state.go('base.deals');
            }).
            error(function(data, status, headers, config) {
                $state.go('base.deals');
            });
    }
]);

/**
 * Controller for creating a deal
 */
dealControllers.controller('DealCreateController', [
    '$scope',

    function($scope) {
        $scope.conf.pageTitleBig = 'New deal';
        $scope.conf.pageTitleSmall = 'making deals';
    }
]);
