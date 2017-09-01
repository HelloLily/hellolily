angular.module('app.contacts').config(contactsConfig);

contactsConfig.$inject = ['$stateProvider'];
function contactsConfig($stateProvider) {
    $stateProvider.state('base.contacts', {
        url: '/contacts',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/list.html',
                controller: ContactListController,
            },
        },
        ncyBreadcrumb: {
            label: 'Contacts',
        },
    });
}

angular.module('app.contacts').controller('ContactListController', ContactListController);

ContactListController.$inject = ['$scope', '$window', 'Settings', 'Account', 'Contact', 'HLUtils', 'LocalStorage'];
function ContactListController($scope, $window, Settings, Account, Contact, HLUtils, LocalStorage) {
    const storage = new LocalStorage('contactList');

    Settings.page.setAllTitles('list', 'contacts');

    /**
     * table object: stores all the information to correctly display the table
     */
    $scope.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: storage.get('filter', ''),  // search filter
        order: storage.get('order', {
            descending: true,
            column: 'modified',  // string: current sorted column
        }),
        visibility: storage.get('visibility', {
            name: true,
            contactInformation: true,
            worksAt: true,
            created: true,
            modified: true,
            tags: true,
        })};
    $scope.showEmptyState = false;

    activate();

    //////

    function activate() {
        showEmptyState();
    }

    $scope.removeFromList = contact => {
        const index = $scope.table.items.indexOf(contact);
        $scope.table.items.splice(index, 1);
        $scope.$apply();
    };

    /**
     * updateTableSettings() puts the scope variables in local storage
     */
    function updateTableSettings() {
        storage.put('filter', $scope.table.filter);
        storage.put('order', $scope.table.order);
        storage.put('visibility', $scope.table.visibility);
    }

    /**
     * updateContacts() reloads the contacts through a service
     *
     * Updates table.items and table.totalItems
     */
    function updateContacts() {
        const blockTarget = '#tableBlockTarget';
        HLUtils.blockUI(blockTarget, true);

        let sort = $scope.table.order.column;

        if ($scope.table.order.descending) {
            sort = '-'.concat(sort);
        }

        Contact.search({
            search: $scope.table.filter,
            page: $scope.table.page,
            page_size: $scope.table.pageSize,
            ordering: sort,
        }, data => {
            $scope.table.items = data.objects;

            $scope.table.items.forEach(contact => {
                if (contact.active_at && contact.accounts) {
                    contact.accounts.forEach(account => {
                        Account.get({id: account.id}, {cache: true}).$promise.then(accountData => {
                            account.primary_email_address = accountData.primary_email_address;
                            account.phone_numbers = accountData.phone_numbers;
                            account.is_active = (contact.active_at.indexOf(account.id) !== -1);
                        });
                    });
                }
            });

            $scope.table.totalItems = data.total;

            HLUtils.unblockUI(blockTarget);
        });
    }

    /**
     * Watches the model info from the table that, when changed,
     * needs a new set of contacts
     */
    $scope.$watchGroup([
        'table.page',
        'table.order.column',
        'table.order.descending',
        'table.filter',
    ], () => {
        updateTableSettings();
        updateContacts();
    });

    /**
     * Watches the model info from the table that, when changed,
     * needs to store the info to the cache
     */
    $scope.$watchCollection('table.visibility', () => {
        updateTableSettings();
    });

    /**
     * setFilter() sets the filter of the table
     *
     * @param queryString string: string that will be set as the new filter on the table
     */
    $scope.setFilter = queryString => {
        $scope.table.filter = queryString;
    };

    /**
     * Count the total amount of contacts used to see whether or not the empty state should be shown.
     */
    function showEmptyState() {
        Contact.query({}, data => {
            if (data.pagination.total === 1) {
                $scope.showEmptyState = true;
            }
        });
    }

    /**
     * exportToCsv() creates an export link and opens it
     */
    $scope.exportToCsv = () => {
        // Setup url.
        let url = '/contacts/export/';
        let getParams = '';

        // If there is a filter, add it.
        if ($scope.table.filter) {
            getParams += '&export_filter=' + $scope.table.filter;
        }

        // Add all visible columns.
        angular.forEach($scope.table.visibility, (value, key) => {
            if (value) {
                getParams += '&export_columns=' + key;
            }
        });

        if (getParams) {
            url += '?' + getParams.substr(1);
        }

        // Open url.
        $window.open(url);
    };
}
