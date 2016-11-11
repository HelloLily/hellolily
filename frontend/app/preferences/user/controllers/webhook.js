angular.module('app.preferences').config(webhookConfig);

webhookConfig.$inject = ['$stateProvider'];
function webhookConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.webhook', {
        url: '/webhook',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/controllers/webhook.html',
                controller: WebhookController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'webhook',
        },
        resolve: {
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('WebhookController', WebhookController);

WebhookController.$inject = ['HLForms', 'HLResource', 'HLUtils', 'user'];
function WebhookController(HLForms, HLResource, HLUtils, user) {
    var vm = this;

    vm.user = user;

    vm.saveWebhooks = saveWebhooks;
    vm.cancelWebhookEditing = cancelWebhookEditing;
    vm.addWebhook = addWebhook;

    function saveWebhooks(form) {
        var formName = '[name="webhookForm"]';
        var args = {
            id: vm.user.id,
            webhooks: vm.user.webhooks,
        };

        HLUtils.blockUI(formName, true);
        HLForms.clearErrors(form);

        HLResource.patch('User', args).$promise.then(function() {
            HLUtils.unblockUI(formName);
        });
    }

    function cancelWebhookEditing() {
        $state.reload();
    }

    function addWebhook() {
        vm.user.webhooks.push({});
    }
}
