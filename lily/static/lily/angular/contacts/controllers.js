/**
 * contactControllers is a container for all contact related Controllers
 */
angular.module('contactControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'contactServices'
])

    /**
     * ContactListController is a controller to show list of contacts
     *
     */
    .controller('ContactListController', [
        '$scope',
        '$cookieStore',
        '$window',

        'Contact',
        'Cookie',
        function($scope, $cookieStore, $window, Contact, Cookie) {

            Cookie.prefix ='contactList';

            /**
             * table object: stores all the information to correctly display the table
             */
            $scope.table = {
                page: 1,  // current page of pagination: 1-index
                pageSize: 20,  // number of items per page
                totalItems: 0, // total number of items
                filter: Cookie.getCookieValue('filter', ''),  // search filter
                order:  Cookie.getCookieValue('order', {
                    ascending: true,
                    column:  'modified'  // string: current sorted column
                }),
                visibility: Cookie.getCookieValue('visibility', {
                    name: true,
                    contactInformation: true,
                    worksAt: true,
                    created: true,
                    modified: true,
                    tags: true
                })};

            /**
             * updateTableSettings() sets scope variables to the cookie
             */
            function updateTableSettings() {
                Cookie.setCookieValue('filter', $scope.table.filter);
                Cookie.setCookieValue('order', $scope.table.order);
                Cookie.setCookieValue('visibility', $scope.table.visibility);
            }

            /**
             * updateContacts() reloads the contacts trough a service
             *
             * Updates table.items and table.totalItems
             */
            function updateContacts() {
                Contact.query(
                    $scope.table
                ).then(function(data) {
                        $scope.table.items = data.contacts;
                        $scope.table.totalItems = data.total;
                    }
                );
            }

            /**
             * Watches the model info from the table that, when changed,
             * needs a new set of contacts
             */
            $scope.$watchGroup([
                'table.page',
                'table.order.column',
                'table.order.ascending',
                'table.filter'
            ], function() {
                updateTableSettings();
                updateContacts();
            });

            /**
             * Watches the model info from the table that, when changed,
             * needs to store the info to the cache
             */
            $scope.$watchCollection('table.visibility', function() {
               updateTableSettings();
            });

            /**
             * setFilter() sets the filter of the table
             *
             * @param queryString string: string that will be set as the new filter on the table
             */
            $scope.setFilter = function(queryString) {
                $scope.table.filter = queryString;
            };

            /**
             * exportToCsv() creates an export link and opens it
             */
            $scope.exportToCsv = function() {
                var getParams = '';

                // If there is a filter, add it
                if ($scope.table.filter) {
                    getParams += '&export_filter=' + $scope.table.filter;
                }

                // Add all visible columns
                angular.forEach($scope.table.visibility, function(value, key) {
                   if (value) {
                       getParams += '&export_columns='+ key;
                   }
                });

                // Setup url
                var url = '/contacts/export/';
                if (getParams) {
                    url += '?' + getParams.substr(1);
                }

                // Open url
                $window.open(url);
            }
        }
    ]
);
