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

EmailListController.$inject = ['$scope', '$state', '$stateParams', 'Settings', 'EmailMessage', 'EmailLabel',
    'EmailAccount', 'LocalStorage', 'SelectedEmailAccount'];
function EmailListController($scope, $state, $stateParams, Settings, EmailMessage, EmailLabel, EmailAccount, LocalStorage, SelectedEmailAccount) {
    var storage = new LocalStorage('inbox');
    var vm = this;

    vm.emailMessages = [];
    vm.primaryEmailAccount = null;
    vm.table = {
        page: Settings.email.page,
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: storage.get('searchQuery', ''),  // search filter
    };
    vm.opts = {
        checkboxesAll: false,
    };

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

    Settings.page.setAllTitles('custom', 'Email');

    activate();

    $scope.$on('$locationChangeSuccess', function() {
        // Reset page if the user clicks an inbox.
        vm.table.page = 0;
    });

    ///////

    function activate() {
        watchTable();
        // Store current email account
        SelectedEmailAccount.setCurrentAccountId($stateParams.accountId);
        SelectedEmailAccount.setCurrentFolderId($stateParams.labelId);
    }

    function setSearchQuery(queryString) {
        vm.table.filter = queryString;
    }

    function watchTable() {
        // Check for search input and pagination
        $scope.$watchGroup([
            'vm.table.filter',
            'vm.table.page',
        ], function(newValues, oldValues) {
            // Reset page if we start searching
            if (oldValues[0] === '' && newValues[0] !== '') {
                vm.setPage(0);
            }

            _updateTableSettings();
            _reloadMessages();
        });
    }

    function _updateTableSettings() {
        storage.put('searchQuery', vm.table.filter);

        Settings.email.page = vm.table.page;
    }

    function setPage(pageNumber) {
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
        var i;

        for (i in vm.emailMessages) {
            if (vm.emailMessages[i].checked) {
                EmailMessage.archive({id: vm.emailMessages[i].id});
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

        if (vm.label.label_id) {
            removedLabels = [vm.label.label_id];
        }

        // Gmail API needs to know the new labels as well as the old ones, so send them too
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
        _reloadMessages();
    }

    function goToDraft(messageId) {
        window.open('/messaging/email/draft/' + messageId + '/', '_self');
    }

    function _reloadMessages() {
        var filterquery = [];

        if ($stateParams.labelId) {
            filterquery.push('label_id:' + $stateParams.labelId);

            if ($stateParams.labelId === 'TRASH') {
                filterquery.push('is_removed:true');
                filterquery.push('is_spam:false'); // like Gmail, don't show deleted spam emails.
            } else if ($stateParams.labelId !== 'SPAM') {
                filterquery.push('is_removed:false');
            }

            if ($stateParams.labelId === 'SPAM') {
                filterquery.push('is_spam:true');
            }
        } else {
            // Corresponds with the 'All mail'-label.
            filterquery.push('NOT label_id:Sent');
            // Exclude removed emails and spam.
            //filterquery.push('is_removed:false'); // TODO: LILY-1812: 'all mail' shows incorrectly deleted mails.
            filterquery.push('is_spam:false');
        }

        if ($stateParams.accountId) {
            filterquery.push('account:' + $stateParams.accountId);

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
            q: vm.table.filter,
            size: vm.table.pageSize,
            page: vm.table.page,
        }, function(data) {
            vm.emailMessages = data.hits;
            vm.table.totalItems = data.total;
        });
    }

    function _normalizeLabel(label) {
        var normalizedLabel = label.toLowerCase();
        return normalizedLabel.charAt(0).toUpperCase() + normalizedLabel.substring(1);
    }
}
