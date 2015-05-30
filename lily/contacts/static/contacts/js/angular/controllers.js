/**
 * ContactsControllers is a container for all case related Controllers
 */
var contacts = angular.module('ContactsControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'app.accounts.services',
    'app.cases.services',
    'contactServices',
    'noteServices',
    'app.email.services'
]);

contacts.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.contacts', {
        url: '/contacts',
        views: {
            '@': {
                templateUrl: 'contacts/contact-list.html',
                controller: 'ContactListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Contacts'
        }
    });
    $stateProvider.state('base.contacts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'contacts/contact-detail.html',
                controller: 'ContactDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ contact.name }}'
        },
        resolve: {
            contact: ['ContactDetail', '$stateParams', function(ContactDetail, $stateParams) {
                var contactId = $stateParams.id;
                return ContactDetail.get({id: contactId}).$promise
            }]
        }
    });
    $stateProvider.state('base.contacts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'contacts/create/',
                controller: 'ContactCreateController'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.contacts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/contacts/edit/' + elem.id +'/';
                },
                controller: 'ContactEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
    $stateProvider.state('base.contacts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'ContactDeleteController'
            }
        },
    });
}]);

contacts.controller('ContactDetailController', ContactDetail);

ContactDetail.$inject = ['$scope', '$stateParams', 'ContactDetail', 'CaseDetail', 'DealDetail', 'contact'];
function ContactDetail($scope, $stateParams, ContactDetail, CaseDetail, DealDetail, contact) {
    var id = $stateParams.id;

    $scope.contact = contact;

    if ($scope.contact.accounts) {
        $scope.contact.accounts.forEach(function(account) {
            var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + id + ') AND accounts.id:' + account.id});
            colleagueList.$promise.then(function(colleagues) {
                account.colleagueList = colleagues;
            })
        });
    }

    $scope.conf.pageTitleBig = 'Contact detail';
    $scope.conf.pageTitleSmall = 'the devil is in the details';

    $scope.caseList = CaseDetail.query({filterquery: 'archived:false AND contact:' + id});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = DealDetail.query({filterquery: 'archived:false AND contact:' + id});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });


}

/**
 * ContactListController is a controller to show list of contacts
 *
 */
contacts.controller('ContactListController', [
    '$scope',
    '$state',
    '$cookieStore',
    '$window',

    'Contact',
    'Cookie',
    'ContactTest',
    function($scope, $state, $cookieStore, $window, Contact, Cookie, ContactTest) {
        var cookie = Cookie('contactList');

        $scope.conf.pageTitleBig = 'Contacts';
        $scope.conf.pageTitleSmall = 'do all your lookin\' here';

        /**
         * table object: stores all the information to correctly display the table
         */
        $scope.table = {
            page: 1,  // current page of pagination: 1-index
            pageSize: 20,  // number of items per page
            totalItems: 0, // total number of items
            filter: cookie.get('filter', ''),  // search filter
            order:  cookie.get('order', {
                ascending: true,
                column:  'modified'  // string: current sorted column
            }),
            visibility: cookie.get('visibility', {
                name: true,
                contactInformation: true,
                worksAt: true,
                created: true,
                modified: true,
                tags: true
            })};

        $scope.deleteContact = function(contact) {
            if (confirm('Are you sure?')) {
                ContactTest.delete({
                    id:contact.id
                }, function() {  // On success
                    var index = $scope.table.items.indexOf(contact);
                    $scope.table.items.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        };

        /**
         * updateTableSettings() sets scope variables to the cookie
         */
        function updateTableSettings() {
            cookie.put('filter', $scope.table.filter);
            cookie.put('order', $scope.table.order);
            cookie.put('visibility', $scope.table.visibility);
        }

        /**
         * updateContacts() reloads the contacts through a service
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
]);

contacts.controller('ContactCreateController', [
    '$scope',

    function($scope) {
        $scope.conf.pageTitleBig = 'New contact';
        $scope.conf.pageTitleSmall = 'who did you talk to?';
    }
]);

contacts.controller('ContactEditController', [
    '$scope',
    '$stateParams',

    'ContactDetail',

    function($scope, $stateParams, ContactDetail) {
        var id = $stateParams.id;
        var contactPromise = ContactDetail.get({id: id}).$promise;

        contactPromise.then(function(contact) {
            $scope.contact = contact;
            $scope.conf.pageTitleBig = contact.name;
            $scope.conf.pageTitleSmall = 'change is natural';
            HLSelect2.init();
        });
    }
]);

/**
 * Controller to delete a contact
 */
contacts.controller('ContactDeleteController', [
    '$state',
    '$stateParams',

    'ContactTest',

    function($state, $stateParams, ContactTest) {
        var id = $stateParams.id;

        ContactTest.delete({
            id:id
        }, function() {  // On success
            $state.go('base.contacts');
        }, function(error) {  // On error
            // Error notification needed
            $state.go('base.contacts');
        });
    }
]);
