angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig ($stateProvider){
    $stateProvider.state('base.email.detail', {
        url: '/detail/{id:[0-9]{1,}}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/detail.html',
                controller: EmailDetailController,
                controllerAs: 'vm'
            }
        }
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);

EmailDetailController.$inject = ['$scope', '$state', '$stateParams', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount'];
function EmailDetailController ($scope, $state, $stateParams, EmailMessage, RecipientInformation, SelectedEmailAccount) {
    var vm = this;
    vm.displayAllRecipients = false;
    vm.message = null;
    vm.archiveMessage = archiveMessage;
    vm.trashMessage = trashMessage;
    vm.deleteMessage = deleteMessage;
    vm.toggleOverlay = toggleOverlay;
    vm.markAsUnread = markAsUnread;
    vm.onlyPlainText = false;

    $scope.conf.pageTitleBig = 'Email message';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    activate();

    //////

    function activate() {
        _getMessage();
    }

    function _getMessage() {
        EmailMessage.get({id: $stateParams.id}, function(result) {
            if (result.body_html) {
                result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
            }else{
                vm.onlyPlainText = true;
            }
            vm.message = result;
            // It's easier to iterate through a single array, so make an array with all recipients
            vm.message.all_recipients = result.received_by.concat(result.received_by_cc);
            // Get contacts
            RecipientInformation.getInformation(vm.message.all_recipients);

            if (!result.read) {
                EmailMessage.markAsRead($stateParams.id, true);
            }
            // Store current email account
            SelectedEmailAccount.setCurrentAccountId(vm.message.account);
        });
    }

    function archiveMessage() {
        EmailMessage.archive({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function trashMessage() {
        EmailMessage.trash({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function deleteMessage () {
        EmailMessage.delete({id: vm.message.id}).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }

    function toggleOverlay () {
        vm.displayAllRecipients = !vm.displayAllRecipients;

        var $emailRecipients = $('.email-recipients');

        if (vm.displayAllRecipients) {
            $emailRecipients.height($emailRecipients[0].scrollHeight);
        } else {
            $emailRecipients.height('1.30em');
        }
    }

    function markAsUnread() {
        EmailMessage.markAsRead(vm.message.id, false).$promise.then(function () {
            $state.go('base.email.list', { 'labelId': 'INBOX' });
        });
    }
}
