angular.module('app.integrations').factory('PandaDoc', PandaDoc);

PandaDoc.$inject = ['$resource'];
function PandaDoc($resource) {
    var _pandadoc = $resource(
        '/api/integrations/pandadoc/',
        null,
        {
            getEvents: {
                url: '/api/integrations/documents/events/',
            },
            saveEvents: {
                method: 'POST',
                url: '/api/integrations/documents/events/',
                isArray: true,
            },
            getSharedKey: {
                method: 'GET',
                url: '/api/integrations/documents/events/shared-key/',
            },
            saveSharedKey: {
                method: 'POST',
                url: '/api/integrations/documents/events/shared-key/',
            },
        }
    );

    _pandadoc.getDocumentEvents = getDocumentEvents;
    _pandadoc.getDocumentStatuses = getDocumentStatuses;

    function getDocumentEvents() {
        return [
            'document_state_changed',
            'recipient_completed',
            'document_updated',
            'document_deleted',
        ];
    }

    function getDocumentStatuses() {
        return [
            'document.uploaded',
            'document.draft',
            'document.sent',
            'document.viewed',
            'document.waiting_approval',
            'document.rejected',
            'document.approved',
            'document.waiting_pay',
            'document.paid',
            'document.completed',
            'document.voided',
        ];
    }

    return _pandadoc;
}
