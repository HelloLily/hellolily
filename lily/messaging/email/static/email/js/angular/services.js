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

    EmailMessage.$inject = ['$resource'];
    function EmailMessage ($resource) {
        return {
            API: $resource(
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
                    }
                }
            ),
            SEARCH: $resource('/search/search/?user_email_related=1&type=email_emailmessage&sort=-sent_date&size=20'),

            markAsRead: function(id, read) {
                this.API.update({id: id, read:read});
            }
        };
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
})();
