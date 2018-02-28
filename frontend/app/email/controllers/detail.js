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
            emailAccount: ['EmailAccount', 'message', (EmailAccount, message) => {
                return EmailAccount.get({id: message.account});
            }],
        },
    });
}

angular.module('app.email').controller('EmailDetail', EmailDetailController);
EmailDetailController.$inject = ['$http', '$scope', '$state', '$stateParams', '$timeout', '$filter', 'Account',
    'Case', 'Deal', 'EmailMessage', 'Settings', 'RecipientInformation', 'SelectedEmailAccount', 'message', 'emailAccount'];
function EmailDetailController($http, $scope, $state, $stateParams, $timeout, $filter, Account, Case, Deal,
    EmailMessage, Settings, RecipientInformation, SelectedEmailAccount, message, emailAccount) {
    var vm = this;

    vm.displayAllRecipients = false;
    vm.message = message;
    vm.onlyPlainText = false;
    vm.emailAccount = emailAccount;

    vm.archiveMessage = archiveMessage;
    vm.trashMessage = trashMessage;
    vm.deleteMessage = deleteMessage;
    vm.toggleOverlay = toggleOverlay;
    vm.markAsUnread = markAsUnread;
    vm.toggleSpam = toggleSpam;
    vm.toggleEmailVariant = toggleEmailVariant;
    vm.showSidebar = showSidebar;
    vm.toggleSidebar = toggleSidebar;
    vm.toggleStarred = toggleStarred;
    vm.moveMessage = moveMessage;
    vm.showMoveToButton = showMoveToButton;

    Settings.page.setAllTitles('custom', 'Email message');

    activate();

    //////

    function activate() {
        var recipients = [];
        var i;

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

                for (i = 0; i < vm.message.all_recipients.length; i++) {
                    recipients.push(vm.message.all_recipients[i].email_address);
                }

                vm.message.recipients = recipients.join(',');

                // Store current email account.
                SelectedEmailAccount.setCurrentAccountId(vm.message.account);

                showSidebar();
            });
        }

        if (Settings.email.previousInbox) {
            vm.currentInbox = Settings.email.previousInbox.params.labelId;
        }

        _watchSidebarVisibility();
    }

    function archiveMessage() {
        var labelToRemove = '';
        var data;

        if (vm.currentInbox) {
            labelToRemove = vm.currentInbox;
        }

        data = {
            current_inbox: labelToRemove,
        };

        EmailMessage.archive({id: vm.message.id, data: data}).$promise.then(function() {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function trashMessage() {
        EmailMessage.trash({id: vm.message.id}).$promise.then(function() {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function deleteMessage() {
        EmailMessage.delete({id: vm.message.id}).$promise.then(function() {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function toggleEmailVariant() {
        vm.onlyPlainText = !vm.onlyPlainText;
    }

    function toggleOverlay() {
        var $emailRecipients = $('.email-recipients');

        vm.displayAllRecipients = !vm.displayAllRecipients;

        if (vm.displayAllRecipients) {
            $emailRecipients.height($emailRecipients[0].scrollHeight);
        } else {
            $emailRecipients.height('1.30em');
        }
    }

    function markAsUnread() {
        EmailMessage.markAsRead(vm.message.id, false).$promise.then(() => {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function moveMessage(labelId) {
        var addedLabels = [labelId];
        var removedLabels = [];
        var data;

        if (vm.currentInbox) {
            removedLabels = [vm.currentInbox];
        }

        // Gmail API needs to know the mutated labels (so both the added and the removed).
        data = {
            remove_labels: removedLabels,
            add_labels: addedLabels,
        };

        EmailMessage.move({id: vm.message.id, data: data}).$promise.then(function() {
            Settings.email.toRemove.push(vm.message);

            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function showSidebar() {
        var filterquery = '';
        var accountQuery = '';
        var accountIds = [];
        var contact;

        Settings.email.data.id = vm.message.id;

        if (vm.message.sender && vm.message.sender.email_address) {
            $http.get('/search/emailaddress/' + vm.message.sender.email_address)
                .success(function(data) {
                    Settings.email.sidebar = {
                        account: true,
                        contact: true,
                        form: null,
                        isVisible: true,
                    };

                    if (!data.free_mail) {
                        Settings.email.data.website = vm.message.sender.email_address.split('@').slice(-1)[0];
                    }

                    if (data && data.data) {
                        if (data.type === 'account') {
                            if (data.data.id) {
                                Settings.email.data.account = data.data;

                                if (!data.complete) {
                                    // Account found, but no contact belongs to account, so setup auto fill data.
                                    Settings.email.sidebar.form = 'contact';
                                    Settings.email.data.account = data.data;
                                }

                                filterquery = 'account.id:' + data.data.id;
                            }
                        } else if (data.type === 'contact') {
                            contact = data.data;

                            if (contact.id) {
                                Settings.email.data.contact = contact;

                                if (contact.accounts && contact.accounts.length) {
                                    if (contact.accounts.length === 1) {
                                        Settings.email.data.account = contact.accounts[0];

                                        filterquery =  'contact.id:' + contact.id + ' OR account.id:' + contact.accounts[0].id;
                                    } else {
                                        angular.forEach(contact.accounts, function(account) {
                                            accountIds.push('id:' + account.id);
                                        });

                                        accountQuery = '(' + accountIds.join(' OR ') + ') AND email_addresses.email_address:' + Settings.email.data.website;

                                        Account.search({filterquery: accountQuery}).$promise.then(function(accountData) {
                                            if (accountData.objects.length) {
                                                // If we get multiple accounts, just pick the first one.
                                                // Additional filter isn't really possible.
                                                Settings.email.data.account = accountData.objects[0];

                                                filterquery =  'contact.id:' + contact.id + ' OR account.id:' + accountData.objects[0].id;
                                            }
                                        });
                                    }
                                } else {
                                    if (!data.free_mail) {
                                        Settings.email.sidebar.form = 'account';
                                    }
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
                        if (data.free_mail) {
                            Settings.email.sidebar.form = 'contact';
                            Settings.email.sidebar.account = false;
                        } else {
                            Settings.email.sidebar.form = 'account';
                            Settings.email.sidebar.contact = false;
                        }
                    }

                    // Setup auto fill contact data in case the user only wants to create a contact.
                    if (data.type !== 'contact') {
                        _setupContactInfo();
                    }
                });
        }
    }

    function _setupContactInfo() {
        let senderParts = vm.message.sender.name.split(' ');

        let account = null;

        if (Settings.email.data.account) {
            account = Settings.email.data.account.id;
        }

        Settings.email.data.contact = {
            firstName: senderParts[0],
            lastName: senderParts.slice(1).join(' '),
            emailAddress: vm.message.sender.email_address,
        };

        // Set the promise so we can resolve it later.
        Settings.email.data.contact.phoneNumbers = EmailMessage.extract({id: vm.message.id, account: account});
    }

    function toggleSidebar(modelName, toggleList) {
        var gaModelName;
        var form = Settings.email.sidebar.form;
        var data = Settings.email.data[modelName];
        var hasData = false;

        // TODO: This is a temporary workaround until we fix the 'Add' button in the list widget.
        // Also remove the toggleList param once we fix it and refactor this.
        if (modelName === 'cases' || modelName === 'deals') {
            _toggleListWidget(modelName, toggleList);
            return;
        }

        Settings.email.sidebar[modelName] = !Settings.email.sidebar[modelName];

        if (data !== null) {
            if (typeof data === 'object' && data.id) {
                hasData = true;
            } else if (typeof data.constructor === Array && data.length) {
                hasData = true;
            }
        }

        if (!hasData && form !== modelName) {
            // Send Google Analytics event when adding new contact/account
            // via email supercards. Use the toggleSidebar function because
            // opening/adding is the same button thus we can differentiate
            // the open and adding actions.
            gaModelName = $filter('ucfirst')(modelName);
            ga('send', 'event', gaModelName, 'Open', 'Email Sidebar');
            // No data yet and no form open, so open the form.
            Settings.email.sidebar.form = modelName;
        } else if (form === modelName) {
            // Form is open, so close it.
            Settings.email.sidebar.form = null;
        }
    }

    function toggleStarred() {
        vm.message.is_starred = !vm.message.is_starred;

        EmailMessage.star({id: vm.message.id, starred: vm.message.is_starred});
    }

    function toggleSpam() {
        vm.message.is_spam = !vm.message.is_spam;

        EmailMessage.spam({id: vm.message.id, markAsSpam: vm.message.is_spam}).$promise.then(function() {
            if (Settings.email.previousInbox) {
                $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
            } else {
                $state.go('base.email.list', {labelId: 'INBOX'});
            }
        });
    }

    function showMoveToButton() {
        let filtered = [];

        if (vm.emailAccount.labels && vm.emailAccount.labels.length) {
            filtered = vm.emailAccount.labels.filter(label => {
                return label.label_type !== 0 && label.label_id !== vm.currentInbox;
            });
        }

        return filtered.length ? true : false;
    }

    function _toggleListWidget(modelName, toggleList) {
        var gaModelName;
        var modelNamePlural = modelName;
        var slicedModelName = modelName.slice(0, 4);

        if (toggleList) {
            Settings.email.sidebar[slicedModelName] = !Settings.email.sidebar[slicedModelName];
        } else {
            if (Settings.email.sidebar.form !== modelNamePlural) {
                // Send Google Analytics event when adding new case or deal via email Sidebar.
                gaModelName = $filter('ucfirst')(modelName);
                // Strip last letter to make modal event singular for Google Analytics naming consistency.
                gaModelName = gaModelName.slice(0, -1);
                ga('send', 'event', gaModelName, 'Open', 'Email Sidebar');
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
        Case.search({filterquery: filterquery, sort: '-created'}, function(data) {
            if (data.objects.length) {
                Settings.email.data.cases = data.objects;
            }
        });
    }

    function _getDeals(filterquery) {
        Deal.search({filterquery: filterquery, sort: '-created'}, function(data) {
            if (data.objects.length) {
                Settings.email.data.deals = data.objects;
            }
        });
    }

    // Broadcast function to send email to trash by HLShortcuts service.
    $scope.$on('deleteMessageByShortCode', function() {
        trashMessage();
    });

    // Broadcast function to archive a specific email by HLShortcuts service.
    $scope.$on('archiveMessageByShortCode', function() {
        archiveMessage();
    });
}
