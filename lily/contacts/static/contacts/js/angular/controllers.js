/**
 * ContactsControllers is a container for all case related Controllers
 */
var contacts = angular.module('ContactsControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'AccountServices',
    'CaseServices',
    'contactServices',
    'noteServices',
    'EmailServices'
]);

contacts.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.contacts', {
        abstract: true,
        url: '/contacts',
        controller: 'ContactBaseController'
    });
    $stateProvider.state('base.contacts.list', {
        url: '',
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
        url: '/{id:[0-9]{1,4}}',
        views: {
            '@': {
                templateUrl: 'contacts/contact-detail.html',
                controller: 'ContactDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ contact.name }}'
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
}]);

contacts.controller('ContactBaseController', [
    '$scope',

    function($scope) {
    }
]);

/**
 * ContactDetailController is a controller to show details of a contact.
 */
contacts.controller('ContactDetailController', [
    'ContactDetail',
    'CaseDetail',
    'NoteDetail',
    'EmailDetail',
    'EmailAccount',
    'ContactTest',
    '$scope',
    '$q',
    '$filter',
    '$stateParams',
    '$state',
    function(ContactDetail, CaseDetail, NoteDetail, EmailDetail, EmailAccount, ContactTest, $scope, $q, $filter, $stateParams, $state) {
        $scope.showMoreText = 'Show more';
        $scope.conf.pageTitleBig = 'Contact detail';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';

        var id = $stateParams.id;

        $scope.deleteContact = function(id) {
            if (confirm('Are you sure?')) {
                ContactTest.delete({
                    id:id
                }, function() {  // On success
                    $state.go('base.contacts.list');
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        };

        function pageTitle(contact) {
            var title = contact.name;
            if (contact.account) {
                title += ' - ' + contact.account_name[0];
            }
            return title;
        }

        var add = 10;
        var size = add;
        var currentSize = 0;
        $scope.history = [];
        function loadHistory(contact, tenantEmails) {
            var notesPromise = NoteDetail.query({
                filterquery: 'content_type:contact AND object_id:' + id,
                size: size
            }).$promise;

            var casesPromise = CaseDetail.query({
                filterquery: 'contact:' + id,
                size: size
            }).$promise;

            var emailAddresses = [];
            if (contact.email) {
                contact.email.forEach(function(emailAddress) {
                    emailAddresses.push(emailAddress);
                });
            }
            var emailPromise = $q.when([]);
            if (emailAddresses.length > 0) {
                var join = emailAddresses.map(function(emailAddress) {
                    // Enclose email addresses with quotes, for exact matching.
                    return '"' + emailAddress + '"';
                }).join(' OR ');
                // Search for correspondence with the user, by checking the email addresses
                // with sent / received headers.
                emailPromise = EmailDetail.query({
                    filterquery: 'sender_email:(' + join + ') OR received_by_email:(' + join + ') OR received_by_cc_email:(' + join + ')',
                    size: size
                }).$promise;
            }
            $q.all([notesPromise, emailPromise, casesPromise]).then(function(results) {
                var history = [];
                var notes = results[0];
                notes.forEach(function(note) {
                    note.note = true;
                    history.push(note);
                });
                var emails = results[1];
                emails.forEach(function(email) {
                    email.email = true;
                    email.date = email.sent_date;
                    email.right = false;
                    // Check if the sender is from tenant.
                    tenantEmails.forEach(function(emailAddress) {
                        if (emailAddress.email_address == email.sender_email) {
                            email.right = true;
                        }
                    });
                    history.push(email);
                });
                var cases = results[2];
                cases.forEach(function(caseItem) {
                    caseItem.caze = true;
                    caseItem.date = caseItem.expires;
                    history.push(caseItem);
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
                else if ($scope.history.length <= currentSize || $scope.history.length < size / 3) {
                    $scope.showMoreText = 'End reached (refresh)';
                }
                currentSize = $scope.history.length;
            });
        }

        var contactPromise = ContactDetail.get({id: id}).$promise;
        contactPromise.then(function(contact) {
            $scope.contact = contact;
            $scope.pageTitle = pageTitle(contact);
            var works = [];
            if (contact.account) {
                contact.account.forEach(function(account_id, index) {
                    var query = {filterquery: 'NOT(id:' + id + ') AND account:' + account_id};
                    var work = ContactDetail.query(query).$promise.then(function(contacts) {
                        return {name:contact.account_name[index], colleagues:contacts};
                    });
                    works.push(work);
                });
            }
            $q.all(works).then(function(results) {
                $scope.works = results;
            });
        });
        var tenantEmailsPromise = EmailAccount.query();
        $scope.loadHistoryFromButton = function() {
            $q.all([contactPromise, tenantEmailsPromise]).then(function(results) {
                loadHistory(results[0], results[1]);
            });
        };
        $scope.loadHistoryFromButton();

        CaseDetail.totalize({filterquery: 'archived:false AND contact:' + id}).$promise.then(function(total) {
            $scope.numCases = total.total;
        });
    }
]);

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
        Cookie.prefix ='contactList';

        $scope.conf.pageTitleBig = 'Contacts';
        $scope.conf.pageTitleSmall = 'do all your lookin\' here';

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
