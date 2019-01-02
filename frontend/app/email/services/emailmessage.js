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
                url: '/search/search/',
                params: {
                    user_email_related: 1,
                    type: 'email_emailmessage',
                    sort: '-sent_date',
                    size: 20,
                },
            },
            searchGmail: {
                method: 'GET',
                url: 'api/messaging/email/search/',
                params: {
                    sort: '-sent_date',
                    size: 20,
                },
                transformResponse: function(data) {
                    // Restructure the data so it matches with the current structure of the elastic search output,
                    // so follow up code is able to handle both.
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    objects.hits  = [];
                    objects.total = 0;

                    if (jsonData) {
                        objects.total = jsonData.total;
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(function(obj) {
                                let emailMessage = $.extend(obj, {
                                    sender_email: obj.sender.email_address,
                                    sender_name: obj.sender.name,
                                    received_by_email: [],
                                });
                                emailMessage.account.email = emailMessage.account.email_address;
                                emailMessage.account.name = emailMessage.account.label;
                                emailMessage.received_by.forEach(function(receiver) {
                                    emailMessage.received_by_email.push(receiver.email_address);
                                });

                                objects.hits.push(emailMessage);
                            });
                        }
                    }

                    return {objects};
                },
            },
            history: {
                method: 'GET',
                url: '/api/messaging/email/email/:id/history/',
                params: {
                    id: '@id',
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
            attachments: {
                url: '/api/messaging/email/email/:id/attachments/',
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
