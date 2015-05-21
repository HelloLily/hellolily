(function() {
    'use strict';

    angular.module('app.preferences.email').config(emailPreferencesStates);

    emailPreferencesStates.$inject = ['$stateProvider'];
    function emailPreferencesStates($stateProvider) {
        $stateProvider.state('base.preferences.emailaccounts.edit', {
            url: '/edit/{id:[0-9]{1,}}',
            views: {
                '@base.preferences': {
                    templateUrl: function (elem, attr) {
                        return 'messaging/email/accounts/update/' + elem.id;
                    },
                    controller: 'PreferencesEmailAccountEdit'
                }
            },
            ncyBreadcrumb: {
                label: 'Edit EmailAccount'
            }
        });
        $stateProvider.state('base.preferences.emailtemplates', {
            url: '/emailtemplates',
            views: {
                '@base.preferences': {
                    templateUrl: 'preferences/emailtemplates-list.html',
                    controller: 'PreferencesEmailTemplatesList'
                }
            },
            ncyBreadcrumb: {
                label: 'Email templates'
            }
        });
        $stateProvider.state('base.preferences.emailtemplates.create', {
            url: '/create',
            views: {
                '@base.preferences': {
                    templateUrl: '/messaging/email/templates/create/',
                    controller: 'PreferencesEmailTemplatesCreate'
                }
            },
            ncyBreadcrumb: {
                label: 'Email template edit'
            }
        });
        $stateProvider.state('base.preferences.emailtemplates.edit', {
            url: '/edit/{id:[0-9]{1,}}',
            views: {
                '@base.preferences': {
                    templateUrl: function(elem, attr) {
                        return '/messaging/email/templates/update/' + elem.id +'/';
                    },
                    controller: 'PreferencesEmailTemplatesEdit'
                }
            },
            ncyBreadcrumb: {
                label: 'Email template create'
            }
        });
    }

    /**
     * PreferencesEmailAccountEdit is a controller to show the base of the settings page.
     */
    angular.module('app.preferences.email')
        .controller('PreferencesEmailAccountEdit', PreferencesEmailAccountEdit);

    function PreferencesEmailAccountEdit () {}

    /**
     * PreferencesEmailTemplatesList is a controller to show the email template list.
     */
    angular.module('app.preferences.email')
        .controller('PreferencesEmailTemplatesList', PreferencesEmailTemplatesList);

    PreferencesEmailTemplatesList.$inject = ['$modal', '$scope', 'EmailTemplate'];
    function PreferencesEmailTemplatesList ($modal, $scope, EmailTemplate) {
        //$scope.conf.pageTitleBig = 'EmailTemplate settings';
        //$scope.conf.pageTitleSmall = 'the devil is in the details';

        EmailTemplate.query({}, function(data) {
            $scope.emailTemplates = data;
        });

        $scope.makeDefault = function(emailTemplate) {
            // TODO: LILY-756: Make this controller more Angular
            var modalInstance = $modal.open({
                templateUrl: '/messaging/email/templates/set-default/' + emailTemplate.id + '/',
                controller: 'PreferencesSetTemplateDefaultModal',
                size: 'lg',
                resolve: {
                    emailTemplate: function () {
                        return emailTemplate;
                    }
                }
            });

            modalInstance.result.then(function () {
                $state.go($state.current, {}, {reload: false});
            }, function () {
            });
        };

        $scope.deleteEmailTemplate = function(emailtemplate) {
            if (confirm('Are you sure?')) {
                EmailTemplate.delete({
                    id: emailtemplate.id
                }, function() {  // On success
                    var index = $scope.emailTemplates.indexOf(emailtemplate);
                    $scope.emailTemplates.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        };
    }

    angular.module('app.preferences.email')
        .controller('PreferencesSetTemplateDefaultModal', PreferencesSetTemplateDefaultModal);

    PreferencesSetTemplateDefaultModal.$inject = ['$http', '$modalInstance', '$scope', 'emailTemplate'];
    function PreferencesSetTemplateDefaultModal ($http, $modalInstance, $scope, emailTemplate) {
        $scope.emailTemplate = emailTemplate;

        $scope.ok = function () {
            $http({
                url: '/messaging/email/templates/set-default/' + $scope.emailTemplate.id + '/',
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                data: $.param({id: $scope.emailTemplate.id})
            }).success(function() {
                $modalInstance.close($scope.emailTemplate);
            });
        };

        // Lets not change anything
        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };
    }
    /**
     * PreferencesEmailTemplatesCreate is a controller to show edit an email template.
     */
    angular.module('app.preferences.email')
        .controller('PreferencesEmailTemplatesCreate', PreferencesEmailTemplatesCreate);

    // TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
    function PreferencesEmailTemplatesCreate () {
        HLInbox.init();
        HLInbox.initWysihtml5();
        HLEmailTemplates.init({
            parseEmailTemplateUrl: '',
            openVariable: '[[',
            closeVariable: ']]'
        });
    }

    /**
     * PreferencesEmailTemplatesEdit is a controller to show edit an email template.
     */
    angular.module('app.preferences.email')
        .controller('PreferencesEmailTemplatesEdit', PreferencesEmailTemplatesEdit);

    // TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
    function PreferencesEmailTemplatesEdit () {
        HLInbox.init();
        HLInbox.initWysihtml5();
        HLEmailTemplates.init({
            parseEmailTemplateUrl: '',
            openVariable: '[[',
            closeVariable: ']]'
        });
    }

    /**
     * EmailAccountShareModal is a controller to show the base of the settings page.
     */
    angular.module('app.preferences.email')
        .controller('EmailAccountShareModal', EmailAccountShareModal);

    EmailAccountShareModal.$inject = ['$modalInstance', '$scope', 'EmailAccount', 'User', 'currentAccount'];
    function EmailAccountShareModal ($modalInstance, $scope, EmailAccount, User, currentAccount) {
        $scope.currentAccount = currentAccount;

        // Get all users to display in a list
        User.query({}, function(data) {
            $scope.users = [];
            // Check if user has the emailaccount already shared
            angular.forEach(data, function(user) {
                if ($scope.currentAccount.shared_with_users.indexOf(user.id) !== -1) {
                    user.sharedWith = true;
                }
                $scope.users.push(user);
            });
        });

        $scope.ok = function () {
            // Save updated account information
            if ($scope.currentAccount.public) {
                EmailAccount.update({id: $scope.currentAccount.id}, $scope.currentAccount, function() {
                    $modalInstance.close();
                });
            } else {
                // Get ids of the users to share with
                var shared_with_users = [];
                angular.forEach($scope.users, function(user) {
                    if(user.sharedWith) {
                        shared_with_users.push(user.id);
                    }
                });
                // Push ids to api
                EmailAccount.shareWith({id: $scope.currentAccount.id}, {shared_with_users: shared_with_users}, function() {
                    $modalInstance.close();
                });
            }
        };

        // Lets not change anything
        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };
    }
})();
