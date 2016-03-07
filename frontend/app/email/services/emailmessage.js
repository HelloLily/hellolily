angular.module('app.email.services').factory('EmailMessage', EmailMessage);

EmailMessage.$inject = ['$resource', '$q'];
function EmailMessage($resource, $q) {
    var _emailMessage = $resource(
        '/api/messaging/email/email/:id/:actions',
        {},
        {
            query: {
                isArray: false,
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: '',
                },
            },
            delete: {
                method: 'DELETE',
                params: {
                    id: '@id',
                    actions: '',
                },
            },
            archive: {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'archive',
                },
            },
            trash: {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'trash',
                },
            },
            get: {
                method: 'GET',
                params: {
                    id: '@id',
                    actions: '',
                },
            },
            move: {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'move',
                },
            },
            star: {
                method: 'PUT',
                params: {
                    id: '@id',
                    actions: 'star',
                },
            },
            search: {
                method: 'GET',
                url: '/search/search/',
                params: {
                    user_email_related: 1,
                    type: 'email_emailmessage',
                    sort: '-sent_date',
                    size: 20,
                },
            },
            history: {
                method: 'GET',
                params: {
                    id: '@id',
                    actions: 'history',
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
