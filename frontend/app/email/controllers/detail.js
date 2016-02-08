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
EmailDetailController.$inject = ['$scope', '$state', '$stateParams', '$http', 'Case', 'Settings', 'Account', 'EmailMessage', 'RecipientInformation', 'SelectedEmailAccount', 'message', 'HLShortcuts'];
function EmailDetailController($scope, $state, $stateParams, $http, Case, Settings, Account, EmailMessage, RecipientInformation, SelectedEmailAccount, message, HLShortcuts) {
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
    vm.toggleSidebar = toggleSidebar;

    Settings.page.setTitle('custom', 'Email message');
    Settings.page.header.setMain('custom', 'Email message');
    Settings.page.header.setSub('email');

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
                // It's easier to iterate through a single array, so make an array with all recipients.
                vm.message.all_recipients = result.received_by.concat(result.received_by_cc);

                // Get contacts.
                RecipientInformation.getInformation(vm.message.all_recipients);

                if (!result.read) {
                    EmailMessage.markAsRead($stateParams.id, true);
                }

                var recipients = [];
                for (var i = 0; i < vm.message.all_recipients.length; i++) {
                    recipients.push(vm.message.all_recipients[i].email_address);
                }

                vm.message.recipients = recipients.join(',');

                // Store current email account.
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
                    Settings.email.sidebar = {
                        account: true,
                        contact: true,
                        form: null,
                        isVisible: true,
                    };

                    Settings.email.data.website = vm.message.sender.email_address.split('@').slice(-1)[0];

                    if (data && data.data) {
                        if (data.type === 'account') {
                            if (data.data.id) {
                                Settings.email.data.account = data.data;

                                if (!data.complete) {
                                    // Account found, but no contact belongs to account, so setup auto fill data.
                                    Settings.email.sidebar.form = 'contact';
                                    Settings.email.data.account = data.data;
                                }

                                var filterquery = 'account:' + data.data.id;
                                _getCases(filterquery);
                            }
                        } else if (data.type === 'contact') {
                            if (data.data.id) {
                                Settings.email.data.contact = data.data;

                                // Check if the contact is linked to an account.
                                Account.searchByEmail({email_address: '@' + Settings.email.data.website}).$promise.then(function(account) {
                                    var filterquery = 'contact:' + data.data.id;

                                    if (account.data && account.data.id) {
                                        Settings.email.data.account = account.data;

                                        filterquery += ' OR account:' + account.data.id;
                                    } else {
                                        Settings.email.sidebar.form = 'account';
                                    }

                                    _getCases(filterquery);
                                });
                            }
                        }

                        Settings.email.sidebar.case = true;
                    } else {
                        Settings.email.sidebar.form = 'account';
                        Settings.email.sidebar.contact = false;

                        // Setup auto fill contact data in case the user only wants to create a contact.
                    }

                    if (data.type !== 'contact') {
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

            for(var i = 1; i < senderParts.length - 1; i++) {
                prepositionParts.push(senderParts[i]);
            }

            preposition = prepositionParts.join(' ');
        }

        Settings.email.data.contact = {
            firstName: senderParts[0],
            preposition: preposition,
            lastName: senderParts[senderParts.length - 1],
            emailAddress: vm.message.sender.email_address,
        };
    }

    function toggleSidebar(modelName, toggleCaseList) {
        // TODO: This is a temporary workaround until we fix the 'Add' button in the list widget.
        // Also remove the toggleCaseList param once we fix it and refactor this.
        if (modelName === 'cases') {
            _toggleCasesSidebar(toggleCaseList);
            return false;
        }

        Settings.email.sidebar[modelName] = !Settings.email.sidebar[modelName];

        var form = Settings.email.sidebar.form;
        var data = Settings.email.data[modelName];
        var hasData = false;

        if (data !== null) {
            if (typeof data === 'object' && data.id) {
                hasData = true;
            } else if (typeof data.constructor === Array && data.length) {
                hasData = true;
            }
        }

        if (!hasData && form !== modelName) {
            // No data yet and no form open, so open the form.
            Settings.email.sidebar.form = modelName;
        } else if (form === modelName) {
            // Form is open, so close it.
            Settings.email.sidebar.form = null;
        }
    }

    function _toggleCasesSidebar(toggleCaseList) {
        if (toggleCaseList) {
            Settings.email.sidebar.case = !Settings.email.sidebar.case;
        } else {
            if (Settings.email.sidebar.form !== 'cases') {
                // No data yet and no form open, so open the form.
                Settings.email.sidebar.form = 'cases';
            } else if (Settings.email.sidebar.form === 'cases') {
                // Form is open, so close it.
                Settings.email.sidebar.form = null;
            }
        }
    }

    function _watchSidebarVisibility() {
        $scope.$watchCollection('settings.email.sidebar', function() {
            Settings.email.sidebar.isVisible = Settings.email.sidebar.account ||
                Settings.email.sidebar.contact || Settings.email.sidebar.cases ||
                Settings.email.sidebar.form;
        });
    }

    function _getCases(filterquery) {
        Case.query({filterquery: filterquery, sort: '-created'}, function(cases) {
            if (cases.length) {
                Settings.email.data.cases = cases;
            }
        });
    }

    // Broadcast function to send e-mail to trash by HLShortcuts service.
    $scope.$on('deleteMessageByShortCode', function() {
        trashMessage();
    });

    // Broadcast function to archive a specific e-mail by HLShortcuts service.
    $scope.$on('archiveMessageByShortCode', function() {
        archiveMessage();
    });
}
