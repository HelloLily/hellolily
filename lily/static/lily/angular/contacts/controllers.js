/**
 * contactControllers is a container for all contact related Controllers
 */
angular.module('contactControllers', [
    'contactServices',
    'ui.bootstrap'
])

    /**
     * ContactListController is a controller to show list of contacts
     *
     */
    .controller('ContactListController', ['$scope', 'Contact', function($scope, Contact) {

        /**
         * table object: stores all the information to correctly display the table
         */
        $scope.table = {
            page: 1, // current page of pagination: 1-index
            pageSize: 20, // number of items per page
            totalItems: 0, // total number of items
            filter: '', // search filter
            order: {
                ascending: true, // 1: descending, 0: ascending
                column: 'modified' // string: current sorted column
            },
            // Columns in table, when true column is visible
            visibility: {
                name: true,
                contactInformation: true,
                worksAt: true,
                created: true,
                modified: true,
                tags: true
            }
        };

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
         * $watchGroup() watches the model info from the table that, when changed,
         * needs a new set of contacts
         */
        $scope.$watchGroup([
            'table.page',
            'table.order.column',
            'table.order.ascending',
            'table.filter'
        ], function() {
            updateContacts();
        });

        /**
         * setFilter() sets the filter of the table
         *
         * @param queryString string: string that will be set as the new filter on the table
         */
        $scope.setFilter = function(queryString) {
            $scope.table.filter = queryString;
        }
    }]
);
