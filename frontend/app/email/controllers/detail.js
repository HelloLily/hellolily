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
        },
        resolve: {
            message: ['EmailMessage', '$stateParams', function(EmailMessage, $stateParams) {
                var id = $stateParams.id;
                return EmailMessage.get({id: id}).$promise;
            }]
        }
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);

EmailDetailController.$inject = ['$scope', '$state', '$stateParams', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount', 'message'];
function EmailDetailController ($scope, $state, $stateParams, EmailMessage, RecipientInformation, SelectedEmailAccount, message) {
    var vm = this;
    vm.displayAllRecipients = false;
    vm.message = message;
    vm.archiveMessage = archiveMessage;
    vm.trashMessage = trashMessage;
    vm.deleteMessage = deleteMessage;
    vm.toggleOverlay = toggleOverlay;
    vm.markAsUnread = markAsUnread;
    vm.onlyPlainText = false;
    vm.toggleEmailVariant = toggleEmailVariant;

    $scope.conf.pageTitleBig = 'Email message';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    //////

    // Load email body after page resolve has finished,
    // so we can already see email headers before the body is loaded.
    message.$promise.then(function(result) {
        if (result.body_html) {
            result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
        }else{
            vm.onlyPlainText = true;
        }
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

    function archiveMessage() {
        EmailMessage.archive({id: vm.message.id}).$promise.then(function () {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            }
            else {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            }
        });
    }

    function trashMessage() {
        EmailMessage.trash({id: vm.message.id}).$promise.then(function () {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            }
            else {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            }
        });
    }

    function deleteMessage () {
        EmailMessage.delete({id: vm.message.id}).$promise.then(function () {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            }
            else {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            }
        });
    }

    function toggleEmailVariant(){
        vm.onlyPlainText = !vm.onlyPlainText;
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
