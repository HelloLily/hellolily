/**
 * dealControllers is a container for all deal related Controllers
 */
angular.module('dealControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'dealServices'
])

    /**
     * DealListController controller to show list of deals
     *
     */
    .controller('DealListController', [
        '$scope',
        '$cookieStore',
        '$window',
        '$location',
        'Deal',
        'Cookie',
        'HLDate',
        function($scope, $cookieStore, $window, $location, Deal, Cookie, HLDate) {

            Cookie.prefix ='dealList';

            // Setup search query
            var searchQuery = '';

            // Check if searchQuery is set as query parameter
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
                pageSize: 20,  // number of items per page
                totalItems: 0, // total number of items
                searchQuery: searchQuery,  // search query
                filterQuery: '',
                archived: Cookie.getCookieValue('archived', false),
                order:  Cookie.getCookieValue('order', {
                    ascending: true,
                    column:  'closing_date'  // string: current sorted column
                }),
                visibility: Cookie.getCookieValue('visibility', {
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
            $scope.filterList = Cookie.getCookieValue('filterList', [
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
                }
            ]);

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
             * updateDeals() reloads the deals trough a service
             *
             * Updates table.items and table.totalItems
             */
            function updateDeals() {
                Deal.query(
                    $scope.table
                ).then(function(data) {
                        $scope.table.items = data.deals;
                        $scope.table.totalItems = data.total;
                    }
                );
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
                $scope.table.filterQuery = '';
                var filterStrings = [];

                for (var i = 0; i < $scope.filterList.length; i++) {
                    var filter = $scope.filterList[i];
                    if (filter.selected) {
                        filterStrings.push(filter.value);
                    }
                }

                $scope.table.filterQuery = filterStrings.join(' AND ');
            }
        }
    ]
);
