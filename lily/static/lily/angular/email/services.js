/**
 * accountServices is a container for all account related Angular services
 */
angular.module('emailServices', [
    'ngResource'
])

    /**
     * $resource for Email model.
     */
    .factory('EmailDetail', ['$resource', function($resource) {
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
    }])

    .factory('EmailAccount', ['$resource', function($resource) {
        return $resource ('/api/messaging/email/account/:id/');
    }])

    .factory('EmailLabel', ['$resource', function($resource) {
        return $resource ('/api/messaging/email/label/:id/');
    }])

    .factory('EmailMessage', ['$resource', 'Cookie', function($resource, Cookie) {
        return {
            API: $resource(
                '/api/messaging/email/email/:id/:actions',
                {},
                {
                    'update': {
                        method: 'PUT',
                        headers: {'X-CSRFToken': Cookie.getCsrftoken()},
                        params: {
                            id: '@id',
                            actions: ''
                        }
                    },
                    'delete': {
                        method: 'DELETE',
                        headers: {'X-CSRFToken': Cookie.getCsrftoken()},
                        params: {
                            id: '@id',
                            actions: ''
                        }
                    },
                    'archive': {
                        method: 'PUT',
                        headers: {'X-CSRFToken': Cookie.getCsrftoken()},
                        params: {
                            id: '@id',
                            actions: 'archive'
                        }
                    },
                    'trash': {
                        method: 'PUT',
                        headers: {'X-CSRFToken': Cookie.getCsrftoken()},
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
                        headers: {'X-CSRFToken': Cookie.getCsrftoken()},
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
    }]);
