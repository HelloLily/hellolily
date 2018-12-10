angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider'];
function emailConfig($stateProvider) {
    $stateProvider.state('base.email.list', {
        url: '/all/{labelId}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.accountAllList', {
        url: '/account/{accountId}/all',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm',
            },
        },
    });
    $stateProvider.state('base.email.accountList', {
        url: '/account/{accountId}/{labelId}',
        views: {
            '@base.email': {
                templateUrl: 'email/controllers/email_list.html',
                controller: EmailListController,
                controllerAs: 'vm',
            },
        },
    });
}

angular.module('app.email').controller('EmailListController', EmailListController);

EmailListController.$inject = ['$scope', '$state', '$stateParams', 'EmailAccount', 'EmailLabel', 'EmailMessage',
    'HLUtils', 'LocalStorage', 'SelectedEmailAccount', 'Settings'];
function EmailListController($scope, $state, $stateParams, EmailAccount, EmailLabel, EmailMessage,
    HLUtils, LocalStorage, SelectedEmailAccount, Settings) {
    var storage = new LocalStorage('inbox');
    var vm = this;

    vm.emailMessages = [];
    vm.primaryEmailAccount = null;
    vm.table = {
        page: Settings.email.page,
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: storage.get('searchQuery', ''),  // search filter
    };
    vm.opts = {
        checkboxesAll: false,
    };
    vm.colorCodes = {};

    vm.showEmptyState = false;
    vm.syncInProgress = false;
    vm.syncMessage = false;

    vm.setPage = setPage;
    vm.toggleCheckboxes = toggleCheckboxes;
    vm.showReplyOrForwardButtons = showReplyOrForwardButtons;
    vm.replyOnMessage = replyOnMessage;
    vm.replyAllOnMessage = replyAllOnMessage;
    vm.forwardOnMessage = forwardOnMessage;
    vm.markAsRead = markAsRead;
    vm.markAsUnread = markAsUnread;
    vm.archiveMessages = archiveMessages;
    vm.trashMessages = trashMessages;
    vm.deleteMessages = deleteMessages;
    vm.moveMessages = moveMessages;
    vm.toggleStarred = toggleStarred;
    vm.starMessages = starMessages;
    vm.reloadMessages = reloadMessages;
    vm.goToDraft = goToDraft;
    vm.setSearchQuery = setSearchQuery;
    vm.handleSelect = handleSelect;
    vm.showMoveToButton = showMoveToButton;

    function handleSelect(index, event) {
        // Keep track of the previously clicked item.
        var i = vm.lastSelected;

        // Set the last selected item.
        vm.lastSelected = index;

        // Check if someone wants to select multiple items.
        if (event.shiftKey) {
            if (i < index) {
                //  We're going from top to bottom, so increment i.
                for (i; i < index; i++) {
                    vm.emailMessages[i].checked = vm.emailMessages[vm.lastSelected].checked;
                }
            } else {
                // Going from bottom to top, so decrement i.
                for (i; i > index; i--) {
                    vm.emailMessages[i].checked = vm.emailMessages[vm.lastSelected].checked;
                }
            }
        }
    }

    Settings.page.setAllTitles('custom', 'Email');

    activate();

    $scope.$on('$locationChangeSuccess', function() {
        // Reset page if the user clicks an inbox.
        vm.table.page = 0;
    });

    ///////

    function activate() {
        HLUtils.blockUI('#emailBase', true);

        watchTable();
        // Store current email account
        SelectedEmailAccount.setCurrentAccountId($stateParams.accountId);
        SelectedEmailAccount.setCurrentFolderId($stateParams.labelId);

        getColorOfEmailAccounts();
    }

    function getColorOfEmailAccounts() {
        EmailAccount.color(results => {
            const colorCodes = {};

            results.forEach(account => {
                let color;

                if (account.color) {
                    color = account.color;
                } else {
                    color = HLUtils.getColorCode(account.email_address);
                }

                colorCodes[account.id] = color;
            });

            vm.colorCodes = colorCodes;

            if (results.length) {
                let synced = results.filter(account => account.is_syncing === false);
                vm.syncInProgress = synced.length ? false : true;
            } else {
                vm.showEmptyState = true;
            }
        });
    }

    function setSearchQuery(queryString) {
        vm.setPage(0);

        vm.table.searchQuery = queryString;
    }

    function watchTable() {
        // Check for search input and pagination
        $scope.$watchGroup([
            'vm.table.searchQuery',
            'vm.table.page',
        ], function(newValues, oldValues) {
            _updateTableSettings();
            _reloadMessages();
        });
    }

    function _updateTableSettings() {
        storage.put('searchQuery', vm.table.searchQuery);

        Settings.email.page = vm.table.page;
    }

    function setPage(pageNumber) {
        HLUtils.blockUI('#emailBase', true);

        if (pageNumber >= 0 && pageNumber * vm.table.pageSize < vm.table.totalItems) {
            vm.table.page = pageNumber;
        }
    }

    function toggleCheckboxes() {
        var i;

        for (i in vm.emailMessages) {
            vm.emailMessages[i].checked = vm.opts.checkboxesAll;
        }
    }

    function _toggleReadMessages(read) {
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.markAsRead(vm.emailMessages[i].id, read);
                vm.emailMessages[i].read = read;
            }
        }
    }

    /**
     * Only show the reply and forward buttons if there is one message checked.
     */
    function showReplyOrForwardButtons() {
        var number = 0;
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                number++;
                if (number > 1) {
                    return false;
                }
            }
        }

        return number === 1;
    }

    /**
     * Get the currently selected EmailMessage instance.
     *
     * @returns EmailMessage instance
     */
    function _selectedMessage() {
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                return vm.emailMessages[i];
            }
        }

        return false;
    }

    /**
     * Reply on selected message.
     */
    function replyOnMessage() {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.reply', {id: message.id});
        }
    }

    /**
     * Reply-all on selected message.
     */
    function replyAllOnMessage() {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.replyAll', {id: message.id});
        }
    }

    /**
     * Forward on selected message.
     */
    function forwardOnMessage() {
        var message = _selectedMessage();
        if (message) {
            $state.go('base.email.forward', {id: message.id});
        }
    }

    function markAsRead() {
        _toggleReadMessages(true);
    }

    function markAsUnread() {
        _toggleReadMessages(false);
    }

    function _removeCheckedMessagesFromList() {
        var i = vm.emailMessages.length;

        while (i--) {
            if (vm.emailMessages[i].checked) {
                vm.emailMessages.splice(i, 1);
            }
        }

        if (vm.opts.checkboxesAll) {
            reloadMessages();
            vm.opts.checkboxesAll = false;
        }
    }

    function archiveMessages() {
        var labelToRemove = '';
        var i;
        var data;

        if (vm.label && vm.label.label_id) {
            labelToRemove = vm.label.label_id;
        }

        data = {
            current_inbox: labelToRemove,
        };

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.archive({id: vm.emailMessages[i].id, data: data});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function trashMessages() {
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.trash({id: vm.emailMessages[i].id});
            }
        }

        _removeCheckedMessagesFromList();
    }

    function deleteMessages() {
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.delete({id: vm.emailMessages[i].id});
            }
        }
        _removeCheckedMessagesFromList();
    }

    function moveMessages(labelId) {
        var addedLabels = [labelId];
        var removedLabels = [];
        var i;
        var data;

        if (vm.label && vm.label.label_id) {
            removedLabels = [vm.label.label_id];
        }

        // Gmail API needs to know the new labels as well as the old ones, so send them too.
        data = {
            remove_labels: removedLabels,
            add_labels: addedLabels,
        };

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.move({id: vm.emailMessages[i].id, data: data});
            }
        }

        _removeCheckedMessagesFromList();
    }

    function toggleStarred(message) {
        message.is_starred = !message.is_starred;

        EmailMessage.star({id: message.id, starred: message.is_starred});
    }

    function starMessages(starred) {
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                vm.emailMessages[i].is_starred = starred;
                EmailMessage.star({id: vm.emailMessages[i].id, starred: starred});
            }
        }
    }

    function reloadMessages() {
        vm.emailMessages = [];

        HLUtils.blockUI('#emailBase', true);

        _reloadMessages();
    }

    function goToDraft(messageId) {
        window.open('/messaging/email/draft/' + messageId + '/', '_self');
    }

    function showMoveToButton() {
        let currentInbox;

        if (vm.label) {
            currentInbox = vm.label.label_id;
        }

        let filtered = vm.account.labels.filter(label => {
            return label.label_type !== 0 && label.label_id !== currentInbox;
        });

        return filtered.length ? true : false;
    }

    function _reloadMessages() {
        var filterquery = [];

        if ($stateParams.labelId) {
            if ($stateParams.labelId === 'INBOX') {
                filterquery.push('is_trashed:false');
                filterquery.push('is_spam:false');
                filterquery.push('is_archived:false');
            } else if ($stateParams.labelId === 'SENT') {
                filterquery.push('label_id:SENT');
                filterquery.push('is_trashed:false');
                filterquery.push('is_spam:false');
            } else if ($stateParams.labelId === 'TRASH') {
                filterquery.push('(is_trashed:true OR is_deleted:false)');
                filterquery.push('is_spam:false');
            } else if ($stateParams.labelId === 'SPAM') {
                filterquery.push('is_spam:true');
                filterquery.push('is_trashed:false');
            } else if ($stateParams.labelId === 'DRAFT') {
                filterquery.push('is_draft:true');
                // Discarded drafts are marked as trashed, so don't show them in the listing anymore.
                filterquery.push('is_trashed:false');
            } else {
                // User labels.
                filterquery.push('label_id:' + $stateParams.labelId);
                filterquery.push('is_trashed:false');
                filterquery.push('is_spam:false');
            }
        } else {
            // Corresponds with the 'All mail'-label.
            filterquery.push('is_trashed:false');
            filterquery.push('is_spam:false');
            filterquery.push('is_draft:false');
        }

        if ($stateParams.accountId) {
            filterquery.push('account.id:' + $stateParams.accountId);

            if ($stateParams.labelId) {
                // Get the label for the given accountId.
                EmailLabel.query({
                    label_id: $stateParams.labelId,
                    account__id: $stateParams.accountId,
                }, function(response) {
                    if (response.results && response.results.length) {
                        vm.label = response.results[0];
                        vm.label.name = _normalizeLabel(vm.label.name);
                    } else {
                        vm.label = {id: $stateParams.labelId, name: _normalizeLabel($stateParams.labelId)};
                    }
                });
            }
            // Get the account for the given accountId.
            vm.account = EmailAccount.get({id: $stateParams.accountId});
        } else {
            vm.label = {id: $stateParams.labelId, name: _normalizeLabel($stateParams.labelId)};
        }

        if (filterquery) {
            filterquery = filterquery.join(' AND ');
        }

        EmailMessage.search({
            filterquery: filterquery,
            q: vm.table.searchQuery,
            size: vm.table.pageSize,
            page: vm.table.page,
        }, function(data) {
            var i;
            var emailMessageIndex = data.hits.length;

            // Make sure changes from the detail view are processed in the front end.
            if (Settings.email.toRemove) {
                while (emailMessageIndex--) {
                    for (i = 0; i < Settings.email.toRemove.length; i++) {
                        if (Settings.email.toRemove[i].id === data.hits[emailMessageIndex].id) {
                            data.hits.splice(emailMessageIndex, 1);
                        }
                    }
                }

                Settings.email.toRemove = [];
            }

            vm.emailMessages = data.hits;
            vm.syncMessage = vm.syncInProgress && data.hits.length === 0;
            vm.table.totalItems = data.total;

            HLUtils.unblockUI('#emailBase');
        });
    }

    function _normalizeLabel(label) {
        var normalizedLabel = label.toLowerCase();
        return normalizedLabel.charAt(0).toUpperCase() + normalizedLabel.substring(1);
    }

    $scope.$on('$viewContentLoaded', () => {
        angular.element('.hl-search-field').focus();
    });
}
