angular.module('app.email.services').factory('EmailTemplateFolder', EmailTemplateFolder);

EmailTemplateFolder.$inject = ['$resource', 'HLResource'];
function EmailTemplateFolder($resource, HLResource) {
    var _emailTemplateFolder = $resource(
        '/api/messaging/email/folders/:id/',
        {},
        {
            query: {
                isArray: false,
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            delete: {
                method: 'DELETE',
            },
        }
    );

    _emailTemplateFolder.updateModel = updateModel;
    _emailTemplateFolder.create = create;

    function create() {
        return new _emailTemplateFolder({
            name: '',
            email_templates: [],
        });
    }

    function updateModel(data, field, folder) {
        let patchPromise;
        const args = HLResource.createArgs(data, field, folder);

        patchPromise = HLResource.patch('EmailTemplateFolder', args).$promise;

        return patchPromise;
    }

    return _emailTemplateFolder;
}
