angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig($stateProvider) {
    $stateProvider.state('base.email.detail', {
        url: '/detail/{id:[0-9]{1,}}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/detail.html',
                controller: EmailDetailController,
                controllerAs: 'vm',
            },
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
            }],
        },
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);
EmailDetailController.$inject = ['$scope', '$state', '$stateParams', '$http', 'AccountDetail', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount', 'message'];
function EmailDetailController($scope, $state, $stateParams, $http, AccountDetail, EmailMessage, RecipientInformation, SelectedEmailAccount, message) {
    var vm = this;
    vm.displayAllRecipients = false;
    vm.message = message;
    vm.onlyPlainText = false;

    vm.archiveMessage = archiveMessage;
    vm.trashMessage = trashMessage;
    vm.deleteMessage = deleteMessage;
    vm.toggleOverlay = toggleOverlay;
    vm.markAsUnread = markAsUnread;
    vm.toggleEmailVariant = toggleEmailVariant;
    vm.showSidebar = showSidebar;
    vm.toggleAccountSidebar = toggleAccountSidebar;
    vm.toggleContactSidebar = toggleContactSidebar;

    $scope.conf.pageTitleBig = 'Email message';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    activate();

    //////

    function activate() {
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
                for (var i = 0; i < vm.message.all_recipients.length; i++) {
                    recipients.push(vm.message.all_recipients[i].email_address);
                }

                vm.message.recipients = recipients.join(',');

                // Store current email account
                SelectedEmailAccount.setCurrentAccountId(vm.message.account);

                showSidebar();
            });
        }

        _watchSidebarVisibility();
    }

    function archiveMessage() {
        EmailMessage.archive({id: vm.message.id}).$promise.then(function() {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function trashMessage() {
        EmailMessage.trash({id: vm.message.id}).$promise.then(function() {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function deleteMessage() {
        EmailMessage.delete({id: vm.message.id}).$promise.then(function() {
            if ($scope.previousState) {
                window.location = $scope.previousState;
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function toggleEmailVariant() {
        vm.onlyPlainText = !vm.onlyPlainText;
    }

    function toggleOverlay() {
        vm.displayAllRecipients = !vm.displayAllRecipients;

        var $emailRecipients = $('.email-recipients');

        if (vm.displayAllRecipients) {
            $emailRecipients.height($emailRecipients[0].scrollHeight);
        } else {
            $emailRecipients.height('1.30em');
        }
    }

    function markAsUnread() {
        EmailMessage.markAsRead(vm.message.id, false).$promise.then(function() {
            $state.go('base.email.list', {labelId: 'INBOX'});
        });
    }

    function showSidebar() {
        if (vm.message.sender && vm.message.sender.email_address) {
            $http.get('/search/emailaddress/' + vm.message.sender.email_address)
                .success(function(data) {
                    $scope.emailSettings.sidebar = {
                        account: true,
                        contact: true,
                        form: null,
                        isVisible: true,
                    };

                    $scope.emailSettings.website = vm.message.sender.email_address.split('@').slice(-1)[0];

                    if (data && data.data) {
                        if (data.type === 'account') {
                            if (data.data.id) {
                                $scope.emailSettings.accountId = data.data.id;

                                if (!data.complete) {
                                    // Account found, but no contact belongs to account, so setup auto fill data
                                    _setupContactInfo();
                                    $scope.emailSettings.sidebar.form = 'createContact';
                                    $scope.emailSettings.account = data.data;
                                }
                            }
                        } else if (data.type === 'contact') {
                            if (data.data.id) {
                                $scope.emailSettings.contactId = data.data.id;

                                var accountsQuery = '';

                                if (data.data.accounts) {
                                    var accountIds = [];

                                    for (var i=0; i < data.data.accounts.length; i++) {
                                        accountIds.push('id:' + data.data.accounts[i].id);
                                    }

                                    accountsQuery = ' AND ' + accountIds.join(' OR ');
                                }

                                // Check if the contact is linked to an account
                                AccountDetail.get({filterquery: 'email_addresses.email_address:"@' + $scope.emailSettings.website + '"' + accountsQuery}).$promise.then(function(account) {
                                    if (account.id) {
                                        $scope.emailSettings.account = account;
                                        $scope.emailSettings.accountId = account.id;
                                    } else {
                                        $scope.emailSettings.sidebar.form = 'createAccount';
                                    }
                                });
                            }
                        }
                    } else {
                        $scope.emailSettings.sidebar.form = 'createAccount';
                        $scope.emailSettings.sidebar.contact = false;

                        // Setup auto fill contact data in case the user only wants to create a contact
                        _setupContactInfo();
                    }
                });
        }
    }

    function _setupContactInfo() {
        // Setup contact name as follows:
        // 1. Split sender name by space
        // 2. First name is always the first element
        // 3. Last name is always the last element
        // 4. Preposition is all other elements
        var senderParts = vm.message.sender.name.split(' ');
        var preposition = '';

        if (senderParts.length > 2) {
            var prepositionParts = [];

            for(var i=1; i < senderParts.length - 1; i++) {
                prepositionParts.push(senderParts[i]);
            }

            preposition = prepositionParts.join(' ');
        }

        $scope.emailSettings.contact = {
            firstName: senderParts[0],
            preposition: preposition,
            lastName: senderParts[senderParts.length - 1],
            emailAddress: vm.message.sender.email_address,
        };
    }

    function toggleAccountSidebar() {
        $scope.emailSettings.sidebar.account = !$scope.emailSettings.sidebar.account;

        if (!$scope.emailSettings.accountId && $scope.emailSettings.sidebar.form !== 'createAccount') {
            // No account set and no form open, so open the account create form
            $scope.emailSettings.sidebar.form = 'createAccount';
            $scope.emailSettings.sidebar.account = true;
            $scope.emailSettings.sidebar.contact = false;
        } else if ($scope.emailSettings.sidebar.form === 'createAccount') {
            // Create account form is open, so close it
            $scope.emailSettings.sidebar.form = null;
            $scope.emailSettings.sidebar.account = false;
        }
    }

    function toggleContactSidebar() {
        $scope.emailSettings.sidebar.contact = !$scope.emailSettings.sidebar.contact;

        if (!$scope.emailSettings.contactId && $scope.emailSettings.sidebar.form !== 'createContact') {
            // No contact set and no form open, so open the contact create form
            $scope.emailSettings.sidebar.form = 'createContact';
            $scope.emailSettings.sidebar.contact = true;
            $scope.emailSettings.sidebar.account = false;
        } else if ($scope.emailSettings.sidebar.form === 'createContact') {
            // Create contact form is open, so close it
            $scope.emailSettings.sidebar.form = null;
            $scope.emailSettings.sidebar.contact = false;
        }
    }

    function _watchSidebarVisibility() {
        $scope.$watchCollection('emailSettings.sidebar', function() {
            $scope.emailSettings.sidebar.isVisible = $scope.emailSettings.sidebar.account || $scope.emailSettings.sidebar.contact || $scope.emailSettings.sidebar.form;
        });
    }
}
