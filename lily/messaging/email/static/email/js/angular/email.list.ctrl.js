(function(){
    'use strict';

    angular.module('app.email').config(emailConfig);
    emailConfig.$inject = ['$stateProvider'];
    function emailConfig($stateProvider) {
        $stateProvider.state('base.email.list', {
            url: '/all/{labelId}',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailList',
                    controllerAs: 'vm'
                }
            }
        });
        $stateProvider.state('base.email.accountAllList', {
            url: '/account/{accountId}/all',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailList',
                    controllerAs: 'vm'
                }
            }
        });
        $stateProvider.state('base.email.accountList', {
            url: '/account/{accountId}/{labelId}',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailList',
                    controllerAs: 'vm'
                }
            }
        });
    }

    /**
     * EmailListController controller to show list of emails
     */
    angular.module('app.email').controller('EmailList', EmailList);

    EmailList.$inject = ['$location', '$scope', '$state', '$stateParams', 'EmailMessage', 'EmailLabel', 'EmailAccount', 'HLText', 'SelectedEmailAccount'];
    function EmailList ($location, $scope, $state, $stateParams, EmailMessage, EmailLabel, EmailAccount, HLText, SelectedEmailAccount) {
        var vm = this;
        vm.emailMessages = [];
        // Check if filter is set as query parameter
        vm.table = {
            page: 0,  // current page of pagination: 1-index
            pageSize: 20,  // number of items per page
            totalItems: 0, // total number of items
            filter: ''  // search filter
        };
        vm.opts = {
            checkboxesAll: false
        };
        vm.primaryEmailAccount = null;
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
        vm.reloadMessages = reloadMessages;
        vm.goToDraft = goToDraft;

        $scope.conf.pageTitleBig = 'Email';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        activate();

        ///////

        function activate() {
            vm.table.filter = $location.search().search || '';
            watchTable();
            // Store current email account
            SelectedEmailAccount.setCurrentAccountId($stateParams.accountId);
        }

        function watchTable() {
            // Check for search input and pagination
            $scope.$watchGroup([
                'vm.table.filter',
                'vm.table.page'
            ], function (newValues, oldValues) {
                // Reset page if we start searching
                if (oldValues[0] == "" && newValues[0] != "") {
                    vm.setPage(0);
                }
                _reloadMessages();
            });
        }

        function setPage(pageNumber) {
            if (pageNumber >= 0 && pageNumber * vm.table.pageSize < vm.table.totalItems) {
                vm.table.page = pageNumber;
            }
        }


        function toggleCheckboxes () {
            for (var i in vm.emailMessages) {
                vm.emailMessages[i].checked = vm.opts.checkboxesAll;
            }
        }

        function _toggleReadMessages(read) {
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    EmailMessage.markAsRead(vm.emailMessages[i].id, read);
                    vm.emailMessages[i].read = read;
                }
            }
        }

        /**
         * Only show the reply and forward buttons if there is one message checked.
         */
        function showReplyOrForwardButtons () {
            var number = 0;
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    number++;
                    if (number > 1) {
                        return false;
                    }
                }
            }
            return number == 1;
        }

        /**
         * Get the currently selected EmailMessage instance.
         *
         * @returns EmailMessage instance
         */
        function _selectedMessage() {
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    return vm.emailMessages[i];
                }
            }
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
        function replyAllOnMessage () {
            var message = _selectedMessage();
            if (message) {
                $state.go('base.email.replyAll', {id: message.id});
            }
        }

        /**
         * Forward on selected message.
         */
        function forwardOnMessage () {
            var message = _selectedMessage();
            if (message) {
                $state.go('base.email.forward', {id: message.id});
            }
        }

        function markAsRead () {
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
        }

        function archiveMessages () {
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    EmailMessage.archive({id: vm.emailMessages[i].id});
                }
            }
            _removeCheckedMessagesFromList();
        }

        function trashMessages () {
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    EmailMessage.trash({id: vm.emailMessages[i].id});
                }
            }
            _removeCheckedMessagesFromList();
        }

        function deleteMessages () {
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    EmailMessage.delete({id: vm.emailMessages[i].id});
                }
            }
            _removeCheckedMessagesFromList();
        }

        function moveMessages (labelId) {
            var removedLabels = [];
            if (vm.label.label_id) {
                removedLabels = [vm.label.label_id];
            }
            var addedLabels = [labelId];
            // Gmail API needs to know the new labels as well as the old ones, so send them too
            var data = {
                remove_labels: removedLabels,
                add_labels: addedLabels
            };
            for (var i in vm.emailMessages) {
                if (vm.emailMessages[i].checked) {
                    EmailMessage.move({id: vm.emailMessages[i].id, data: data});
                }
            }
            _removeCheckedMessagesFromList();
        }

        function reloadMessages () {
            vm.emailMessages = [];
            _reloadMessages();
        }

        function goToDraft (messageId) {
            window.open('/messaging/email/draft/' + messageId + '/', '_self');
        }

        function _reloadMessages() {
            var filterquery = [];

            if ($stateParams.labelId) {
                filterquery.push('label_id:' + $stateParams.labelId);
            } else {
                filterquery.push('NOT label_id:Sent');
            }

            if ($stateParams.accountId) {
                filterquery.push('account:' + $stateParams.accountId);

                if ($stateParams.labelId) {
                    // Get the label for the given accountId
                    EmailLabel.query({
                        label_id: $stateParams.labelId,
                        account__id: $stateParams.accountId
                    }, function (results) {
                        if (results.length) {
                            vm.label = results[0];
                            vm.label.name = vm.label.name.hlCapitalize();
                        } else {
                            vm.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()};
                        }
                    });
                }
                // Get the account for the given accountId
                vm.account = EmailAccount.get({id: $stateParams.accountId});
            } else {
                vm.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()};
            }

            if ($stateParams.labelId && $stateParams.labelId != 'TRASH') {
                filterquery.push('is_removed:false');
            }

            if (filterquery) {
                filterquery = filterquery.join(' AND ');
            }

            EmailMessage.search({
                filterquery: filterquery,
                q: vm.table.filter,
                size: vm.table.pageSize,
                page: vm.table.page
            }, function (data) {
                vm.emailMessages = data.hits;
                vm.table.totalItems = data.total;
            });
        }
    }
})();

