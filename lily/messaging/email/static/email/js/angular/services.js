(function() {
    /**
     * app.email.services is a container for all email related Angular services
     */
    angular.module('app.email.services', ['ngResource']);

    /**
     * $resource for Email model.
     */
    angular.module('app.email.services').factory('EmailDetail', EmailDetail);

    EmailDetail.$inject = ['$resource'];
    function EmailDetail ($resource) {
        return $resource(
            '',
            {size:100},
            {
                query: {
                    url: '/search/search/?type=email_emailmessage&size=:size&sort=-sent_date&filterquery=:filterquery&account_related=:account_related',
                    isArray: true,
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        var objects = [];
                        if (data && data.hits && data.hits.length > 0) {
                            data.hits.forEach(function(obj) {
                                obj = $.extend(obj, {historyType: 'email', color: 'green', date: obj.sent_date, right: false});
                                objects.push(obj)
                            });
                        }
                        return objects;
                    }
                }
            }
        );
    }

    angular.module('app.email.services').factory('EmailAccount', EmailAccount);

    EmailAccount.$inject = ['$resource'];
    function EmailAccount ($resource) {
        return $resource('/api/messaging/email/account/:id/', null,
            {
                'update': { method: 'PUT' },
                'shareWith': {
                    method: 'POST',
                    url: '/api/messaging/email/account/:id/shared/'
                }
            });
    }

    angular.module('app.email.services').factory('EmailTemplate', EmailTemplate);

    EmailTemplate.$inject = ['$resource'];
    function EmailTemplate ($resource) {
        return $resource('/api/messaging/email/emailtemplate/:id/');
    }

    angular.module('app.email.services').factory('EmailLabel', EmailLabel);

    EmailLabel.$inject = ['$resource'];
    function EmailLabel ($resource) {
        return $resource('/api/messaging/email/label/:id/');
    }

    angular.module('app.email.services').factory('EmailMessage', EmailMessage);

    EmailMessage.$inject = ['$resource', '$q'];
    function EmailMessage ($resource, $q) {
        var EmailMessage = $resource(
            '/api/messaging/email/email/:id/:actions',
            {},
            {
                'update': {
                    method: 'PUT',
                    params: {
                        id: '@id',
                        actions: ''
                    }
                },
                'delete': {
                    method: 'DELETE',
                    params: {
                        id: '@id',
                        actions: ''
                    }
                },
                'archive': {
                    method: 'PUT',
                    params: {
                        id: '@id',
                        actions: 'archive'
                    }
                },
                'trash': {
                    method: 'PUT',
                    params: {
                        id: '@id',
                        actions: 'trash'
                    }
                },
                'get': {
                    method: 'GET',
                    params: {
                        id: '@id',
                        actions: ''
                    }
                },
                'move': {
                    method: 'PUT',
                    params: {
                        id: '@id',
                        actions: 'move'
                    }
                },
                'search': {
                    method: 'GET',
                    url: '/search/search/',
                    params: {
                        user_email_related: 1,
                        type: 'email_emailmessage',
                        sort: '-sent_date',
                        size: 20
                    }
                }
            }
        );

        EmailMessage.markAsRead = markAsRead;
        EmailMessage.getDashboardMessages = getDashboardMessages;

        //////

        function markAsRead (id, read) {
            return this.update({id: id, read: read});
        }

        function getDashboardMessages (field, sorting) {
            var filterQuery = ['read:false AND label_id:INBOX'];
            var sort = '';
            sort += sorting ? '-': '';
            sort += field;

            var deferred = $q.defer();
            EmailMessage.search({
                filterquery: filterQuery,
                sort: sort
            }, function (data) {
                deferred.resolve(data.hits);
            });
            return deferred.promise;
        }
        return EmailMessage
    }

    /**
     * SelectedEmailAccount is a service that keeps track of the current selected EmailAccount
     */

    angular.module('app.email.services').factory('SelectedEmailAccount', SelectedEmailAccount);

    function SelectedEmailAccount () {

        var factory = {
            currentAccountId: null,
            setCurrentAccountId: setCurrentAccountId
        };
        return factory;

        function setCurrentAccountId (accountId) {
            factory.currentAccountId = accountId;
        }
    }

    angular.module('app.email.services').factory('RecipientInformation', RecipientInformation);

    RecipientInformation.$inject = ['$http'];
    function RecipientInformation ($http) {

        var RecipientInformation = {};

        RecipientInformation.getInformation = getInformation;

        //////

        function getInformation(recipients) {
            recipients.forEach(function (recipient) {
                // If there's a name set, try to get the contact id
                // Don't set/change the name because we want to keep the original email intact
                if (recipient.name != '') {
                    $http.get('/search/emailaddress/' + recipient.email_address)
                        .success(function (data) {
                            if (data.type == 'contact') {
                                if (data.data.id) {
                                    recipient.contact_id = data.data.id;
                                }
                            }
                        });
                }
            });
        }

        return RecipientInformation;
    }
})();
