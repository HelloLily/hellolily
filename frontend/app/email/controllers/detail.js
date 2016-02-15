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
EmailDetailController.$inject = ['$http', '$scope', '$state', '$stateParams', '$timeout', 'Account', 'Case', 'Deal',
    'EmailMessage', 'Settings', 'RecipientInformation', 'SelectedEmailAccount', 'message'];
function EmailDetailController($http, $scope, $state, $stateParams, $timeout, Account, Case, Deal, EmailMessage,
                               Settings, RecipientInformation, SelectedEmailAccount, message) {
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
                        var filterquery = '';

                        if (data.type === 'account') {
                            if (data.data.id) {
                                Settings.email.data.account = data.data;

                                if (!data.complete) {
                                    // Account found, but no contact belongs to account, so setup auto fill data.
                                    Settings.email.sidebar.form = 'contact';
                                    Settings.email.data.account = data.data;
                                }

                                filterquery = 'account:' + data.data.id;
                            }
                        } else if (data.type === 'contact') {
                            var contact = data.data;

                            if (contact.id) {
                                Settings.email.data.contact = contact;

                                if (contact.accounts && contact.accounts.length) {
                                    if (contact.accounts.length === 1) {
                                        Settings.email.data.account = contact.accounts[0];

                                        filterquery =  'contact:' + contact.id + ' OR account:' + contact.accounts[0].id;
                                    } else {
                                        var accountIds = [];

                                        angular.forEach(contact.accounts, function(account) {
                                            accountIds.push('id:' + account.id);
                                        });

                                        var accountQuery = '(' + accountIds.join(' OR ') + ') AND email_addresses.email_address:' + Settings.email.data.website;

                                        Account.search({filterquery: accountQuery}).$promise.then(function(accounts) {
                                            if (accounts.length) {
                                                // If we get multiple accounts, just pick the first one.
                                                // Additional filter isn't really possible.
                                                Settings.email.data.account = accounts[0];

                                                filterquery =  'contact:' + contact.id + ' OR account:' + accounts[0].id;
                                            }
                                        });
                                    }
                                } else {
                                    Settings.email.sidebar.form = 'account';
                                }
                            }
                        }

                        // We could add the _getCases call everywhere, but we'd be repeating ourselves.
                        // Instead just wait until the filterquery is set and then load the cases/deals.
                        $timeout((function() {
                            function checkFilterQuery() {
                                if (!filterquery) {
                                    $timeout(checkFilterQuery);
                                } else {
                                    _getCases(filterquery);
                                    _getDeals(filterquery);
                                }
                            }

                            return checkFilterQuery;
                        })());

                        Settings.email.sidebar.case = true;
                        Settings.email.sidebar.deal = true;
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

    function toggleSidebar(modelName, toggleList) {
        // TODO: This is a temporary workaround until we fix the 'Add' button in the list widget.
        // Also remove the toggleList param once we fix it and refactor this.
        if (modelName === 'cases' || modelName === 'deals') {
            _toggleListWidget(modelName, toggleList);
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

    function _toggleListWidget(modelName, toggleList) {
        var modelNamePlural = modelName;
        modelName = modelName.slice(0, 4);

        if (toggleList) {
            Settings.email.sidebar[modelName] = !Settings.email.sidebar[modelName];
        } else {
            if (Settings.email.sidebar.form !== modelNamePlural) {
                // No data yet and no form open, so open the form.
                Settings.email.sidebar.form = modelNamePlural;
            } else if (Settings.email.sidebar.form === modelNamePlural) {
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

    function _getDeals(filterquery) {
        Deal.query({filterquery: filterquery, sort: '-created'}, function(deals) {
            if (deals.length) {
                Settings.email.data.deals = deals;
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
