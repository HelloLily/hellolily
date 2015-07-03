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
                return EmailMessage.get({id: id}).$promise.then(function(message) {
                    return message;
                }, function() {
                    // In case the email does not exist, return empty message.
                    return {};
                });
            }]
        }
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);

EmailDetailController.$inject = ['$scope', '$state', '$stateParams', '$http', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount'];
function EmailDetailController ($scope, $state, $stateParams, $http, EmailMessage, RecipientInformation, SelectedEmailAccount) {
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
    vm.showSidebar = showSidebar;
    vm.showCreateAccountSidebar = showCreateAccountSidebar;

    $scope.conf.pageTitleBig = 'Email message';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    //////

    // Load email body after page resolve has finished,
    // so we can already see email headers before the body is loaded.
    if (message.id) {
        message.$promise.then(function(result) {
            if (result.body_html) {
                result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
            } else {
                vm.onlyPlainText = true;
            }
            // It's easier to iterate through a single array, so make an array with all recipients
            vm.message.all_recipients = result.received_by.concat(result.received_by_cc);

            // Get contacts
            RecipientInformation.getInformation(vm.message.all_recipients);

            if (!result.read) {
                EmailMessage.markAsRead($stateParams.id, true);
            }

            var recipients = [];
            for(var i = 0; i < vm.message.all_recipients.length; i++){
                recipients.push(vm.message.all_recipients[i].email_address);
            }

            vm.message.recipients = recipients.join(',');

            // Store current email account
            SelectedEmailAccount.setCurrentAccountId(vm.message.account);

            showSidebar();
        });
    }

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

    function showSidebar() {
        if (vm.message.sender && vm.message.sender.email_address) {
            $http.get('/search/emailaddress/' + vm.message.sender.email_address)
                .success(function (data) {
                    $scope.emailSettings.sideBar = false;
                    if (data && data.data && data.type == 'contact') {
                        $scope.emailSettings.sideBar = false
                    } else if ((data && data.data && !data.complete) ||
                        (Object.getOwnPropertyNames(data).length === 0)) {
                        $scope.emailSettings.sideBar = 'hasNoAccount';
                        $scope.emailSettings.emailAddress = vm.message.sender.email_address;
                        var website = vm.message.sender.email_address.split('@');
                        website = website.slice(-1)[0];
                        var company = website.split('.');
                        company = company.slice(0, -1);
                        company = company.join(' ');
                        $scope.emailSettings.company = company;
                        $scope.emailSettings.website = website;
                    } else if (data && data.data && data.complete) {
                        $scope.emailSettings.sideBar = 'hasAccount';
                        $scope.emailSettings.accountId = data.data.id;
                    }
                });
        }
    }

    function showCreateAccountSidebar() {
        if ($scope.emailSettings.sideBar == 'hasNoAccount') {
            $scope.emailSettings.sideBar = 'createAccount';
        } else if ($scope.emailSettings.sideBar == 'createAccount') {
            $scope.emailSettings.sideBar = 'hasNoAccount';
        } else if ($scope.emailSettings.sideBar == 'hasAccount') {
            $scope.emailSettings.sideBar = 'showAccount';
        } else if ($scope.emailSettings.sideBar == 'showAccount') {
            $scope.emailSettings.sideBar = 'hasAccount';
        }
    }
}
