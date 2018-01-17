angular.module('app.email.services').factory('EmailMessage', EmailMessage);

EmailMessage.$inject = ['$resource', '$q'];
function EmailMessage($resource, $q) {
    var _emailMessage = $resource(
        '/api/messaging/email/email/:id/',
        {},
        {
            query: {
                isArray: false,
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            delete: {
                method: 'DELETE',
                params: {
                    id: '@id',
                },
            },
            archive: {
                method: 'PUT',
                url: '/api/messaging/email/email/:id/archive/',
                params: {
                    id: '@id',
                },
            },
            trash: {
                method: 'PUT',
                url: '/api/messaging/email/email/:id/trash/',
                params: {
                    id: '@id',
                },
            },
            get: {
                method: 'GET',
                params: {
                    id: '@id',
                },
            },
            move: {
                method: 'PUT',
                url: '/api/messaging/email/email/:id/move/',
                params: {
                    id: '@id',
                },
            },
            star: {
                method: 'PUT',
                url: '/api/messaging/email/email/:id/star/',
                params: {
                    id: '@id',
                },
            },
            search: {
                method: 'GET',
                url: 'api/messaging/email/search/',
                params: {
                    sort: '-sent_date',
                    size: 20,
                },
            },
            spam: {
                method: 'PUT',
                url: '/api/messaging/email/email/:id/spam/',
                params: {
                    id: '@id',
                },
            },
            extract: {
                method: 'POST',
                url: '/api/messaging/email/email/:id/extract/',
                params: {
                    id: '@id',
                },
            },
        }
    );

    _emailMessage.markAsRead = markAsRead;

    //////

    function markAsRead(id, read) {
        return this.update({id: id, read: read});
    }

    return _emailMessage;
}
