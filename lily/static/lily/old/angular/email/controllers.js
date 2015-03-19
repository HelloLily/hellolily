/**
 * emailControllers is a container for all account related Controllers
 */
angular.module('emailControllers', [
    // 3rd party
    'ui.bootstrap',
    'ui.router',

    // Lily dependencies
    'emailServices',
    'lilyServices'
])
    .config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider){
        $stateProvider
            .state('email', {
                abstract: true,
                url: '',
                templateUrl: '/messaging/email/label_list.html/',
                controller: 'EmailController'
            })
            .state('email.list', {
                url: '/all/{labelId}',
                templateUrl: '/messaging/email/email_list.html/',
                controller: 'EmailListController'
            })
            .state('email.accountAllList', {
                url: '/account/{accountId}/all',
                templateUrl: '/messaging/email/email_list.html/',
                controller: 'EmailListController'
            })
            .state('email.accountList', {
                url: '/account/{accountId}/{labelId}',
                templateUrl: '/messaging/email/email_list.html/',
                controller: 'EmailListController'
            })
            .state('email.detail', {
                url: '/detail/{id:int}',
                templateUrl: '/messaging/email/email_detail.html/',
                controller: 'EmailDetailController'
            });

        $urlRouterProvider.otherwise('/all/inbox');
    }])
    .controller('EmailController', [
        '$location',
        '$scope',

        function($location, $scope) {

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
    }])

    /**
     * EmailListController controller to show list of accounts
     */
    .controller('EmailListController', [
        '$scope',
        '$stateParams',

        'EmailMessage',
        'EmailLabel',
        'EmailAccount',

        'HLText',
        function($scope, $stateParams, EmailMessage, EmailLabel, EmailAccount, HLText) {

            $scope.table.page = 0;
            $scope.table.filter = '';
            $scope.opts = { checkboxesAll: false};

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

                if ($scope.table.filter) {
                    filterquery = '';
                } else if ($stateParams.accountId) {
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
    ])

    /**
     * EmailListController controller to show list of accounts
     */
    .controller('EmailDetailController', [
        '$scope',
        '$state',
        '$stateParams',
        'EmailMessage',
        function($scope, $state, $stateParams, EmailMessage) {
            EmailMessage.API.get({id: $stateParams.id}, function(result) {
                if (result.body_html) {
                    result.bodyHTMLUrl = '/messaging/email/html/' + result.id + '/';
                }
                $scope.message = result;

                if (!result.read) {
                    EmailMessage.markAsRead($stateParams.id, true);
                }
            });

            $scope.archiveMessage = function() {
                EmailMessage.API.archive({id: $scope.message.id});
                $state.go('email.list', '');
            };

            $scope.trashMessage = function() {
                EmailMessage.API.trash({id: $scope.message.id});
                $state.go('email.list', '');
            };

            $scope.deleteMessage = function() {
                EmailMessage.API.delete({id: $scope.message.id});
                $state.go('email.list', '');
            }
        }
    ])

    /**
     * LabelListController controller to show list of labels for different accounts
     */
    .controller('LabelListController', [
        '$scope',

        'EmailAccount',
        function($scope, EmailAccount) {

            $scope.getAccountInfo = function() {
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

                    // Check every 60 seconds if there are new emails
                    setTimeout($scope.getAccountInfo, 6000);
                });

            };
            // Initial load
            $scope.getAccountInfo();

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
    }]);
