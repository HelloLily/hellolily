/**
 * caseControllers is a container for all case related Controllers
 */
var contacts = angular.module('ContactsControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    //'accountServices',
    'contactServices',
    //'caseServices',
    //'noteServices',
    //'emailServices'
]);

/**
 * ContactDetailController is a controller to show details of a contact.
 */
//contacts.controller('ContactDetailController', [
//    'ContactDetail',
//    'CaseDetail',
//    'NoteDetail',
//    'EmailDetail',
//    'EmailAccount',
//    '$scope',
//    '$q',
//    '$filter',
//    function(Contact, Case, Note, Email, EmailAccount, $scope, $q, $filter) {
//        $scope.showMoreText = 'Show more';
//        var id = window.location.pathname;
//        if (id.substr(-1) == '/') {
//            id = id.substr(0, id.length - 1);
//        }
//        id = id.substr(id.lastIndexOf('/') + 1);
//
//        function pageTitle(contact) {
//            var title = contact.name;
//            if (contact.account) {
//                title += ' - ' + contact.account_name[0];
//            }
//            return title;
//        }
//
//        var add = 10;
//        var size = add;
//        var currentSize = 0;
//        $scope.history = [];
//        function loadHistory(contact, tenantEmails) {
//            var notesPromise = Note.query({
//                filterquery: 'content_type:contact AND object_id:' + id,
//                size: size
//            }).$promise;
//
//            var casesPromise = Case.query({
//                filterquery: 'contact:' + id,
//                size: size
//            }).$promise;
//
//            var emailAddresses = [];
//            if (contact.email) {
//                contact.email.forEach(function(emailAddress) {
//                    emailAddresses.push(emailAddress);
//                });
//            }
//            var emailPromise = $q.when([]);
//            if (emailAddresses.length > 0) {
//                var join = emailAddresses.map(function(emailAddress) {
//                    // Enclose email addresses with quotes, for exact matching.
//                    return '"' + emailAddress + '"';
//                }).join(' OR ');
//                // Search for correspondence with the user, by checking the email addresses
//                // with sent / received headers.
//                emailPromise = Email.query({
//                    filterquery: 'sender_email:(' + join + ') OR received_by_email:(' + join + ') OR received_by_cc_email:(' + join + ')',
//                    size: size,
//                }).$promise;
//            }
//            $q.all([notesPromise, emailPromise, casesPromise]).then(function(results) {
//                var history = [];
//                var notes = results[0];
//                notes.forEach(function(note) {
//                    note.note = true;
//                    history.push(note);
//                });
//                var emails = results[1];
//                emails.forEach(function(email) {
//                    email.email = true;
//                    email.date = email.sent_date;
//                    email.right = false;
//                    // Check if the sender is from tenant.
//                    tenantEmails.forEach(function(emailAddress) {
//                        if (emailAddress.email_address == email.sender_email) {
//                            email.right = true;
//                        }
//                    });
//                    history.push(email);
//                });
//                var cases = results[2];
//                cases.forEach(function(caseItem) {
//                    caseItem.caze = true;
//                    caseItem.date = caseItem.expires;
//                    history.push(caseItem);
//                });
//
//                $scope.history.splice(0, $scope.history.length);
//                $filter('orderBy')(history, 'date', true).forEach(function(item) {
//                    $scope.history.push(item);
//                });
//                $scope.history.splice(size, $scope.history.length);
//                size += add;
//                if ($scope.history.length == 0) {
//                    $scope.showMoreText = 'No history (refresh)';
//                }
//                else if ($scope.history.length <= currentSize || $scope.history.length < size / 3) {
//                    $scope.showMoreText = 'End reached (refresh)';
//                }
//                currentSize = $scope.history.length;
//            });
//        }
//
//        var contactPromise = Contact.get({id: id}).$promise;
//        contactPromise.then(function(contact) {
//            $scope.contact = contact;
//            $scope.pageTitle = pageTitle(contact);
//            var works = [];
//            if (contact.account) {
//                contact.account.forEach(function(account_id, index) {
//                    var query = {filterquery: 'NOT(id:' + id + ') AND account:' + account_id};
//                    var work = Contact.query(query).$promise.then(function(contacts) {
//                        return {name:contact.account_name[index], colleagues:contacts};
//                    });
//                    works.push(work);
//                });
//            }
//            $q.all(works).then(function(results) {
//                $scope.works = results;
//            });
//        });
//        var tenantEmailsPromise = EmailAccount.query();
//        $scope.loadHistoryFromButton = function() {
//            $q.all([contactPromise, tenantEmailsPromise]).then(function(results) {
//                loadHistory(results[0], results[1]);
//            });
//        };
//        $scope.loadHistoryFromButton();
//
//        Case.totalize({filterquery: 'archived:false AND contact:' + id}).$promise.then(function(total) {
//            $scope.numCases = total.total;
//        });
//    }
//]);

/**
 * ContactListController is a controller to show list of contacts
 *
 */
contacts.controller('ContactListController', [
    '$scope',
    '$cookieStore',
    '$window',

    'Contact',
    'Cookie',
    function($scope, $cookieStore, $window, Contact, Cookie) {
        console.log('contact list');
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
]);

contacts.config(['$stateProvider', function($stateProvider) {
    $stateProvider
        .state('base.contacts', {
            url: '/contacts/',
            templateUrl: 'contacts/contact-list.html',
            controller: 'ContactListController'
        });
}]);
