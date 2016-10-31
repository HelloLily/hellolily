angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailtemplates', {
        url: '/emailtemplates',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/email/controllers/emailtemplate_list.html',
                controller: PreferencesEmailTemplatesList,
                controllerAs: 'vm',
                bindToController: true,
            },
        },
        ncyBreadcrumb: {
            label: 'Email templates',
        },
    });
}

angular.module('app.preferences').controller('PreferencesEmailTemplatesList', PreferencesEmailTemplatesList);

PreferencesEmailTemplatesList.$inject = ['$compile', '$scope', '$state', '$templateCache', 'EmailAccount', 'EmailTemplate'];
function PreferencesEmailTemplatesList($compile, $scope, $state, $templateCache, EmailAccount, EmailTemplate) {
    var vm = this;

    vm.makeDefault = makeDefault;
    vm.removeFromList = removeFromList;

    activate();

    //////

    function activate() {
        getTemplates();
    }

    function getTemplates() {
        EmailTemplate.query({}, function(data) {
            vm.emailTemplates = data.results;
        });
    }

    function makeDefault(emailTemplate) {
        EmailAccount.mine().$promise.then(function(emailAccounts) {
            vm.emailAccounts = emailAccounts;

            vm.emailAccounts.forEach(function(emailAccount) {
                // For every email account in emailTemplate.default_for set selected to true.
                var selected = emailTemplate.default_for.filter(function(accountId) {
                    return accountId === emailAccount.id;
                });

                emailAccount.selected = selected.length > 0;
            });

            swal({
                html: $compile($templateCache.get('preferences/email/controllers/emailtemplate_default.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(function(isConfirm) {
                var args = emailTemplate;
                var selectedAccounts = [];

                if (isConfirm) {
                    // Loop over email accounts to extract the selected accounts.
                    vm.emailAccounts.forEach(function(emailAccount) {
                        if (emailAccount.selected) {
                            selectedAccounts.push(emailAccount.id);
                        }
                    });

                    args.default_for = selectedAccounts;

                    EmailTemplate.update(args).$promise.then(function() {
                        getTemplates();
                        swal.close();
                        toastr.success('I\'ve updated the email template for you!', 'Done');
                    }, function(response) {
                        HLForms.setErrors(form, response.data);
                        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                    });
                }
            }).done();
        });
    }

    function removeFromList(emailtemplate) {
        var index = vm.emailTemplates.indexOf(emailtemplate);
        vm.emailTemplates.splice(index, 1);

        $scope.$apply();
    }
}
