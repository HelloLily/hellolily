/**
 * emailControllers is a container for all email related Controllers
 */
var EmailControllers = angular.module('EmailControllers', [
    // 3rd party
    'ui.bootstrap',
    'ui.router',

    // Lily dependencies
    'EmailServices',
    'EmailDirectives',
    'LilyServices'
]);

EmailControllers.config([
    '$stateProvider',
    function($stateProvider){
        $stateProvider.state('base.email', {
            abstract: true,
            url: '/email',
            views: {
                '@': {
                    templateUrl: 'email/base.html',
                    controller: 'EmailController'
                },
                'labelList@base.email': {
                    templateUrl: 'email/label_list.html',
                    controller: 'LabelListController'
                }
            },
            ncyBreadcrumb: {
                label: 'Email'
            }
        });
        $stateProvider.state('base.email.list', {
            url: '/all/{labelId}',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailListController'
                }
            }
        });
        $stateProvider.state('base.email.accountAllList', {
            url: '/account/{accountId}/all',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailListController'
                }
            }
        });
        $stateProvider.state('base.email.accountList', {
            url: '/account/{accountId}/{labelId}',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_list.html',
                    controller: 'EmailListController'
                }
            }
        });
        $stateProvider.state('base.email.detail', {
            url: '/detail/{id:[0-9]{1,}}',
            views: {
                '@base.email': {
                    templateUrl: 'email/email_detail.html',
                    controller: 'EmailDetailController'
                }
            }
        });
        // TODO: LILY-XXX: Clean up compose states and make email/template optional params
        $stateProvider.state('base.email.compose', {
            url: '/compose',
            views: {
                '@base.email': {
                    templateUrl: '/messaging/email/compose/',
                    controller: 'EmailComposeController'
                }
            }
        });
        $stateProvider.state('base.email.composeEmail', {
            url: '/compose/{email}',
            views: {
                '@base.email': {
                    templateUrl: '/messaging/email/compose/',
                    controller: 'EmailComposeController'
                }
            }
        });
        $stateProvider.state('base.email.composeEmailTemplate', {
            url: '/compose/{email}/{template}',
            views: {
                '@base.email': {
                    templateUrl: '/messaging/email/compose/',
                    controller: 'EmailComposeController'
                }
            }
        });
        $stateProvider.state('base.email.reply', {
            url: '/reply/{id:[0-9]{1,}}',
            params: {
                messageType: 'reply'
            },
            views: {
                '@base.email': {
                    templateUrl: function(elem, attr) {
                        return '/messaging/email/reply/' + elem.id + '/';
                    },
                    controller: 'EmailComposeController'
                }
            }
        });
        $stateProvider.state('base.email.replyAll', {
            // TODO: This should probably be redone so the url is nicer.
            // Maybe we can save the action in the scope?
            url: '/replyall/{id:[0-9]{1,}}',
            params: {
                messageType: 'reply-all'
            },
            views: {
                '@base.email': {
                    templateUrl: function(elem, attr) {
                        return '/messaging/email/replyall/' + elem.id + '/';
                    },
                    controller: 'EmailComposeController'
                }
            }
        });
        $stateProvider.state('base.email.forward', {
            url: '/forward/{id:[0-9]{1,}}',
            params: {
                messageType: 'forward'
            },
            views: {
                '@base.email': {
                    templateUrl: function(elem, attr) {
                        return '/messaging/email/forward/' + elem.id + '/';
                    },
                    controller: 'EmailComposeController'
                }
            }
        });
    }
]);

EmailControllers.controller('EmailController', [
    '$location',
    '$scope',
    function($location, $scope) {

        $scope.conf.pageTitleBig = 'Email';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        // Setup filter
        var filter = '';

        // Check if filter is set as query parameter
        var search = $location.search().search;
        if (search != undefined) {
            filter = search;
        }

        $scope.table = {
            page: 0,  // current page of pagination: 1-index
            pageSize: 20,  // number of items per page
            totalItems: 0, // total number of items
            filter: filter  // search filter
        };

        $scope.setPage = function(pageNumber) {
            if (pageNumber >= 0 && pageNumber * $scope.table.pageSize < $scope.table.totalItems) {
                $scope.table.page = pageNumber;
            }
        };
    }
]);

/**
 * EmailListController controller to show list of emails
 */
EmailControllers.controller('EmailListController', [
    '$scope',
    '$state',
    '$stateParams',
    'EmailMessage',
    'EmailLabel',
    'EmailAccount',
    'HLText',
    function($scope, $state, $stateParams, EmailMessage, EmailLabel, EmailAccount, HLText) {
        $scope.conf.pageTitleBig = 'Email';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        $scope.table.page = 0;
        $scope.table.filter = '';
        $scope.opts = {checkboxesAll: false};

        $scope.toggleCheckboxes = function() {
            for (var i in $scope.emailMessages) {
                $scope.emailMessages[i].checked = $scope.opts.checkboxesAll;
            }
        };

        function toggleReadMessages(read) {
            for (var i in $scope.emailMessages) {
                if ($scope.emailMessages[i].checked) {
                    EmailMessage.markAsRead($scope.emailMessages[i].id, read);
                    $scope.emailMessages[i].read = read;
                }
            }
        }

        /**
         * Only show the reply and forward buttons if there is one message checked.
         */
        $scope.showReplyOrForwardButtons = function() {
            var number = 0;
            for (var i in $scope.emailMessages) {
                if($scope.emailMessages[i].checked) {
                    number++;
                    if (number > 1) {
                        return false;
                    }
                }
            }
            return number == 1;
        };

        /**
         * Get the currently selected EmailMessage instance.
         *
         * @returns EmailMessage instance
         */
        function selectedMessage() {
            for (var i in $scope.emailMessages) {
                if($scope.emailMessages[i].checked) {
                    return $scope.emailMessages[i];
                }
            }
        }

        /**
         * Reply on selected message.
         */
        $scope.replyOnMessage = function() {
            var message = selectedMessage();
            if(message) {
                $state.go('base.email.reply', {id: message.id});
            }
        };

        /**
        * TODO: LILY-706: Reply-all on selected message.
        */
        $scope.replyAllOnMessage = function() {
            var message = selectedMessage();
            if(message) {
                $state.go('base.email.replyAll', {id: message.id});
            }
        };

        /**
        * TODO: LILY-707: Forward on selected message.
        */
        $scope.forwardOnMessage = function() {
            var message = selectedMessage();
            if(message) {
                $state.go('base.email.forward', {id: message.id});
            }
        };

        $scope.markAsRead = function() {
            toggleReadMessages(true);
        };

        $scope.markAsUnread = function() {
            toggleReadMessages(false);
        };

        function removeCheckedMessagesFromList() {
            var i = $scope.emailMessages.length;
            while (i--) {
                if ($scope.emailMessages[i].checked) {
                    $scope.emailMessages.splice(i, 1);
                }
            }
        }

        $scope.archiveMessages = function() {
            for (var i in $scope.emailMessages) {
                if ($scope.emailMessages[i].checked) {
                    EmailMessage.API.archive({id: $scope.emailMessages[i].id});
                }
            }
            removeCheckedMessagesFromList();
        };

        $scope.trashMessages = function() {
            for (var i in $scope.emailMessages) {
                if ($scope.emailMessages[i].checked) {
                    EmailMessage.API.trash({id: $scope.emailMessages[i].id});
                }
            }
            removeCheckedMessagesFromList();
        };

        $scope.deleteMessages = function() {
            for (var i in $scope.emailMessages) {
                if ($scope.emailMessages[i].checked) {
                    EmailMessage.API.delete({id: $scope.emailMessages[i].id});
                }
            }
            removeCheckedMessagesFromList();
        };

        $scope.moveMessages = function(labelId) {
            var removedLabels = [];
            if ($scope.label.label_id) {
                removedLabels = [$scope.label.label_id];
            }
            var addedLabels = [labelId];
            // Gmail API needs to know the new labels as well as the old ones, so send them too
            var data = {
                remove_labels: removedLabels,
                add_labels: addedLabels
            };
            for (var i in $scope.emailMessages) {
                if ($scope.emailMessages[i].checked) {
                    EmailMessage.API.move({id: $scope.emailMessages[i].id, data: data});
                }
            }
            removeCheckedMessagesFromList();
        };

        // Check for search input and pagination
        $scope.$watchGroup([
            'table.filter',
            'table.page'
        ], function(newValues, oldValues) {
            // Reset page if we start searching
            if (oldValues[0] == "" && newValues[0] != "") {
                $scope.setPage(0);
            }
            reloadMessages();
        });

        $scope.reloadMessages = function() {
            $scope.emailMessages = [];
            reloadMessages();
        };

        $scope.goToDraft = function(messageId) {
            window.open('/messaging/email/draft/' + messageId + '/', '_self');
        };

        function reloadMessages() {
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
                            $scope.label = results[0];
                            $scope.label.name = $scope.label.name.hlCapitalize();
                        } else {
                            $scope.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()};
                        }
                    });
                }
                // Get the account for the given accountId
                $scope.account = EmailAccount.get({id: $stateParams.accountId});
            } else {
                $scope.label = {id: $stateParams.labelId, name: $stateParams.labelId.hlCapitalize()}
            }

            if ($stateParams.labelId && $stateParams.labelId != 'TRASH') {
                filterquery.push('is_removed:false');
            }

            if (filterquery) {
                filterquery = filterquery.join(' AND ');
            }

            EmailMessage.SEARCH.get({
                filterquery: filterquery,
                q: $scope.table.filter,
                size: $scope.table.pageSize,
                page: $scope.table.page
            }, function(data) {
                $scope.emailMessages = data.hits;
                $scope.table.totalItems = data.total;
            });
        }
    }
]);

/**
 * EmailDetailcontroller controller to show an emailmessage
 */
EmailControllers.controller('EmailDetailController', [
    '$scope',
    '$state',
    '$stateParams',
    'EmailMessage',
    function($scope, $state, $stateParams, EmailMessage) {

        $scope.conf.pageTitleBig = 'Email message';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        $scope.displayAllRecipients = false;

        EmailMessage.API.get({id: $stateParams.id}, function(result) {
            if (result.body_html) {
                result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
            }
            $scope.message = result;
            // It's easier to iterate through a single array, so make an array with all recipients
            $scope.message.all_recipients = result.received_by.concat(result.received_by_cc);

            if (!result.read) {
                EmailMessage.markAsRead($stateParams.id, true);
            }
        });

        $scope.archiveMessage = function() {
            EmailMessage.API.archive({id: $scope.message.id}).$promise.then(function () {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            });
        };

        $scope.trashMessage = function() {
            EmailMessage.API.trash({id: $scope.message.id}).$promise.then(function () {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            });
        };

        $scope.deleteMessage = function() {
            EmailMessage.API.delete({id: $scope.message.id}).$promise.then(function () {
                $state.go('base.email.list', { 'labelId': 'INBOX' });
            });
        };

        $scope.toggleOverlay = function () {
            $scope.displayAllRecipients = !$scope.displayAllRecipients;

            var $emailRecipients = $('.email-recipients');

            if ($scope.displayAllRecipients) {
                $emailRecipients.height($emailRecipients[0].scrollHeight);
            }
            else {
                $emailRecipients.height('1.30em');
            }
        };
    }
]);

/**
 * LabelListController controller to show list of labels for different accounts
 */
EmailControllers.controller('LabelListController', [
    '$interval',
    '$scope',
    'EmailAccount',
    function($interval, $scope, EmailAccount) {

        // Fetch the EmailAccounts & associated labels
        var getAccountInfo = function() {
            EmailAccount.query(function(results) {
                $scope.accountList = results;
                var labelCount = {};
                for (var i in $scope.accountList){
                    for (var j in $scope.accountList[i].labels) {
                        var label = $scope.accountList[i].labels[j];
                        if (label.label_type == 0) {
                            if (labelCount.hasOwnProperty(label.label_id)) {
                                labelCount[label.label_id] += parseInt(label.unread);
                            } else {
                                labelCount[label.label_id] = parseInt(label.unread);
                            }
                        }
                    }
                }
                $scope.labelCount = labelCount;
            });
        };

        //Fetch again every 60 seconds
        getAccountInfo();
        var stopGetAccountInfo = $interval(getAccountInfo, 60000);

        // Stop fetching when out of scope
        $scope.$on('$destroy', function() {
            // Make sure that the interval is destroyed too
            if (angular.isDefined(stopGetAccountInfo)) {
                $interval.cancel(stopGetAccountInfo);
                stopGetAccountInfo = undefined;
            }
        });

        function unreadCountForLabel(account, labelId) {
            var count = 0;
            angular.forEach(account.labels, function(label, key) {
               if (label.label_id == labelId) {
                   count = label.unread;
                   return true
               }
            });
            return count;
        }

        $scope.hasUnreadLabel = function(account, labelId) {
            return unreadCountForLabel(account, labelId) > 0;

        };

        $scope.unreadCountForLabel = function(account, labelId) {
            return unreadCountForLabel(account, labelId);
        }
    }
]);

EmailControllers.controller('EmailComposeController', [
    '$scope',
    '$stateParams',
    '$q',
    'ContactDetail',
    'EmailMessage',
    'EmailTemplate',
    function ($scope, $stateParams, $q, ContactDetail, EmailMessage, EmailTemplate) {
        $scope.conf.pageTitleBig = 'Send email';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        if ($stateParams.messageType == 'reply') {
            // If it's a reply, load the email message first
            EmailMessage.API.get({id: $stateParams.id}).$promise.then(function (emailMessage) {
                initEmailCompose(emailMessage);
            });
        }
        else {
            // Otherwise just initialize the email compose
            initEmailCompose();
        }

        function initEmailCompose(emailMessage) {
            var email = $stateParams.email;

            var promises = [];

            var recipient = null;
            var contactPromise;

            if (emailMessage) {
                contactPromise = ContactDetail.query({filterquery: 'email:' + emailMessage.sender.email_address}).$promise;
                promises.push(contactPromise);
            }
            else if (email) {
                contactPromise = ContactDetail.query({filterquery: 'email:' + email}).$promise;
                promises.push(contactPromise);
            }

            var emailTemplatePromise = EmailTemplate.query().$promise;
            promises.push(emailTemplatePromise);

            // TODO: LILY-XXX: Check if this can be cleaned up
            // Once all promises are done, continue
            $q.all(promises).then(function(results) {
                var templates;
                // This part should only be executed if we've loaded a contact
                if(contactPromise) {
                    var contact = results[0][0];
                    templates = results[1];

                    if (emailMessage) {
                        email = emailMessage.sender.email_address;
                    }

                    if (contact) {
                        // The text which is actually used in the application/select2
                        var used_text = '"' + contact.name + '" <' + email + '>';
                        // The text shown in the recipient input
                        var displayed_text = contact.name + ' <' + email + '>';

                        recipient = {
                            id: used_text,
                            text: displayed_text,
                            object_id: contact.id
                        };
                    }
                    else {
                        recipient = {
                            id: email,
                            text: email,
                            object_id: null
                        };
                    }
                } else {
                    templates = results[0];
                }

                var template = $stateParams.template;
                // Determine whether the default template should be loaded or not
                var loadDefaultTemplate = template == undefined;

                // Set message type to given message type if available, otherwise set to message type 'new'
                var messageType = $stateParams.messageType ? $stateParams.messageType : 'new';

                HLInbox.init();
                HLInbox.initEmailCompose({
                    templateList: templates,
                    defaultEmailTemplateUrl: '/messaging/email/templates/get-default/',
                    getTemplateUrl: '/messaging/email/templates/detail/',
                    messageType: messageType,
                    loadDefaultTemplate: loadDefaultTemplate,
                    recipient: recipient,
                    template: template
                });
            });
        }
    }
]);
