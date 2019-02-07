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

PreferencesEmailTemplatesList.$inject = ['$compile', '$scope', '$state', '$templateCache', 'EmailAccount',
    'EmailTemplate', 'EmailTemplateFolder', 'Settings'];
function PreferencesEmailTemplatesList($compile, $scope, $state, $templateCache, EmailAccount,
    EmailTemplate, EmailTemplateFolder, Settings) {
    const vm = this;

    Settings.page.setAllTitles('list', 'email templates');

    vm.templateFolders = [];
    vm.newFolder = EmailTemplateFolder.create();

    vm.getTemplates = getTemplates;
    vm.makeDefault = makeDefault;
    vm.removeTemplate = removeTemplate;
    vm.addFolder = addFolder;
    vm.updateFolderName = updateFolderName;
    vm.moveTemplates = moveTemplates;
    vm.checkSelected = checkSelected;

    activate();

    //////

    function activate() {
        getTemplates();
    }

    function getTemplates() {
        EmailTemplateFolder.query().$promise.then(templateFolders => {
            let templateCount = 0;

            templateFolders.results.map(folder => {
                templateCount += folder.email_templates.length;
            });

            vm.templateFolders = templateFolders.results;

            vm.templateCount = templateCount;

            EmailTemplate.query({folder__isnull: 'True'}).$promise.then(templates => {
                vm.templateFolders.push({
                    name: 'Not in folder',
                    email_templates: templates.results,
                });

                vm.templateCount += templates.results.length;
            });
        });
    }

    function makeDefault(emailTemplate) {
        EmailAccount.mine().$promise.then(emailAccounts => {
            vm.emailAccounts = emailAccounts;

            vm.emailAccounts.forEach(emailAccount => {
                // For every email account in emailTemplate.default_for set selected to true.
                let selected = emailTemplate.default_for.filter(accountId => {
                    return accountId === emailAccount.id;
                });

                emailAccount.selected = selected.length > 0;
            });

            swal({
                html: $compile($templateCache.get('preferences/email/controllers/emailtemplate_default.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(isConfirm => {
                let args = emailTemplate;
                let selectedAccounts = [];

                if (isConfirm) {
                    // Loop over email accounts to extract the selected accounts.
                    vm.emailAccounts.map(emailAccount => {
                        if (emailAccount.selected) {
                            selectedAccounts.push(emailAccount.id);
                        }
                    });

                    args.default_for = selectedAccounts;

                    EmailTemplate.update(args).$promise.then(() => {
                        swal.close();
                        toastr.success('I\'ve updated the email template for you!', 'Done');
                    }, response => {
                        HLForms.setErrors(form, response.data);
                        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                    });
                }
            }).done();
        });
    }

    function removeTemplate(folder, template) {
        let index = folder.email_templates.indexOf(template);
        folder.email_templates.splice(index, 1);

        $scope.$apply();
    }

    function addFolder() {
        vm.newFolder.$save(response => {
            toastr.success('Folder has been saved', 'Done');

            vm.templateFolders.unshift(response);
            vm.newFolder = EmailTemplateFolder.create();
        });
    }

    function updateFolderName(data, folder) {
        const field = 'name';

        return EmailTemplateFolder.updateModel(data, field, folder);
    }

    function moveTemplates(folder) {
        let moveTo = folder ? folder.id : null;

        if (vm.templateIds.length) {
            EmailTemplate.move({templates: vm.templateIds, folder: moveTo}).$promise.then(() => {
                toastr.success('Email templates have been moved', 'Done');

                getTemplates();
            });
        }
    }

    function checkSelected() {
        let templateIds = [];

        vm.templateFolders.map(templateFolder => {
            templateFolder.email_templates.map(template => {
                if (template.selected) {
                    templateIds.push(template.id);
                }
            });
        });

        vm.templateIds = templateIds;
    }
}
