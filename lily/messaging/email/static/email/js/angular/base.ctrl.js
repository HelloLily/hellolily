(function() {
    'use strict';

    angular.module('app.email').config(emailConfig);
    emailConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
    function emailConfig($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.when('/email', '/email/all/INBOX');
        $stateProvider.state('base.email', {
            url: '/email',
            views: {
                '@': {
                    templateUrl: 'email/base.html',
                    controller: 'EmailBase',
                    controllerAs: 'vm'
                },
                'labelList@base.email': {
                    templateUrl: 'email/label_list.html',
                    controller: 'LabelList',
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'Email'
            },
            resolve: {
                primaryEmailAccountId: ['$q', 'User', function($q, User) {
                    var deferred = $q.defer();
                    User.me(null, function(data) {
                        deferred.resolve(data.primary_email_account);
                    });
                    return deferred.promise;
                }]
            }
        });
    }

    angular.module('app.email').controller('EmailBase', EmailBase);

    EmailBase.$inject = ['$scope'];
    function EmailBase($scope) {
        var vm = this;

        $scope.conf.pageTitleBig = 'Email';
        $scope.conf.pageTitleSmall = 'sending love through the world!';

        activate();

        //////////

        function activate() {}
    }

    angular.module('app.email').controller('LabelList', LabelList);

    LabelList.$inject = ['$filter', '$interval', '$scope', 'EmailAccount', 'primaryEmailAccountId'];
    function LabelList($filter, $interval, $scope, EmailAccount, primaryEmailAccountId) {
        var vm = this;
        vm.accountList = [];
        vm.primaryEmailAccountId = primaryEmailAccountId;
        vm.labelCount = 0;
        vm.hasUnreadLabel = hasUnreadLabel;
        vm.unreadCountForLabel = unreadCountForLabel;

        activate();

        //////////

        function activate() {
            _startIntervalAccountInfo();
        }

        function _startIntervalAccountInfo() {
            _getAccountInfo();
            var stopGetAccountInfo = $interval(_getAccountInfo, 60000);

            // Stop fetching when out of scope
            $scope.$on('$destroy', function() {
                // Make sure that the interval is destroyed too
                if (angular.isDefined(stopGetAccountInfo)) {
                    $interval.cancel(stopGetAccountInfo);
                    stopGetAccountInfo = undefined;
                }
            });
        }

        // Fetch the EmailAccounts & associated labels
        function _getAccountInfo () {
            EmailAccount.query(function (results) {
                // Sort accounts on id
                results = $filter('orderBy')(results, 'id');

                vm.accountList = [];
                // Make sure primary account is set first
                angular.forEach(results, function(account) {
                    if (account.id != vm.primaryEmailAccountId) {
                        this.push(account);
                    } else {
                        this.unshift(account);
                    }
                }, vm.accountList);

                // Check for unread email count
                var labelCount = {};
                for (var i in vm.accountList) {
                    for (var j in vm.accountList[i].labels) {
                        var label = vm.accountList[i].labels[j];
                        if (label.label_type == 0) {
                            if (labelCount.hasOwnProperty(label.label_id)) {
                                labelCount[label.label_id] += parseInt(label.unread);
                            } else {
                                labelCount[label.label_id] = parseInt(label.unread);
                            }
                        }
                    }
                }
                vm.labelCount = labelCount;
            });
        }

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

        function hasUnreadLabel (account, labelId) {
            return unreadCountForLabel(account, labelId) > 0;

        }
    }
})();
