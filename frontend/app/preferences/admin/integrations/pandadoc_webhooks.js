angular.module('app.preferences').config(pandaDocWebhooks);

pandaDocWebhooks.$inject = ['$stateProvider'];
function pandaDocWebhooks($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.pandadoc.webhooks', {
        url: '/webhooks',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/pandadoc_webhooks.html',
                controller: PandaDocWebhooksController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            tenant: ['Tenant', Tenant => Tenant.query({})],
            nextSteps: ['Deal', Deal => Deal.getNextSteps().$promise],
            statuses: ['Deal', Deal => Deal.getStatuses().$promise],
            events: ['PandaDoc', PandaDoc => PandaDoc.getEvents().$promise],
            sharedKey: ['PandaDoc', PandaDoc => PandaDoc.getSharedKey().$promise],
        },
    });
}

angular.module('app.preferences').controller('PandaDocWebhooksController', PandaDocWebhooksController);

PandaDocWebhooksController.$inject = ['$state', 'HLForms', 'PandaDoc', 'nextSteps', 'statuses', 'tenant', 'events', 'sharedKey'];
function PandaDocWebhooksController($state, HLForms, PandaDoc, nextSteps, statuses, tenant, events, sharedKey) {
    const vm = this;

    vm.sharedKey = sharedKey.shared_key;
    vm.nextSteps = nextSteps.results;
    vm.statusChoices = statuses.results;
    vm.eventChoices = PandaDoc.getDocumentEvents();
    vm.documentStatusChoices = PandaDoc.getDocumentStatuses();
    vm.tenant = tenant;
    vm.events = events.results.length ? events.results : [{}];

    vm.saveForm = saveForm;
    vm.cancel = cancel;
    vm.saveSharedKey = saveSharedKey;
    vm.addRow = addRow;
    vm.getName = getName;

    function saveForm(form) {
        HLForms.blockUI();

        PandaDoc.saveEvents(vm.events).$promise.then(response => {
            toastr.success('The PandaDoc events have been saved', 'Done');
            $state.reload();
        }, error => {
            toastr.error(error.data.duplicate_event, 'Oops');
            Metronic.unblockUI();
        });
    }

    function saveSharedKey() {
        HLForms.blockUI();

        PandaDoc.saveSharedKey({shared_key: vm.sharedKey}).$promise.then(response => {
            toastr.success('Your PandaDoc shared key has been saved', 'Done');
            $state.reload();
        }, error => {
            toastr.error('Something went wrong', 'Oops');
            Metronic.unblockUI();
        });
    }

    function addRow() {
        vm.events.push({});
    }

    function getName(name) {
        // Clean up the name so it's human readable.
        // This means we remove the document_ and document. from the name.
        // Also replace any remaining underscores with spaces.
        const newName = name.replace(/document_|document\./g, '').replace('_', ' ');
        return newName.charAt(0).toUpperCase() + newName.slice(1);
    }

    function cancel() {
        $state.reload();
    }
}
