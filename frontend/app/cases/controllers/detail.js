angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases.detail', {
        parent: 'base.cases',
        url: '/{id:int}',
        views: {
            '@': {
                templateUrl: 'cases/controllers/detail.html',
                controller: CaseDetailController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: '{{ case.subject }}',
        },
        resolve: {
            currentCase: ['Case', '$stateParams', (Case, $stateParams) => Case.get({id: $stateParams.id}).$promise],
            caseAccount: ['Account', 'currentCase', (Account, currentCase) => {
                let account;

                if (currentCase.account) {
                    account = Account.get({id: currentCase.account.id, filter_deleted: 'False'}).$promise;
                }

                return account;
            }],
            caseContact: ['Contact', 'currentCase', (Contact, currentCase) => {
                let contact;

                if (currentCase.contact) {
                    contact = Contact.get({id: currentCase.contact.id, filter_deleted: 'False'}).$promise;
                }

                return contact;
            }],
            timeLogs: ['TimeLog', 'currentCase', (TimeLog, currentCase) => {
                return TimeLog.getForObject({id: currentCase.id, model: 'cases'}).$promise;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$scope', 'Case', 'HLResource', 'HLUtils', 'LocalStorage', 'Settings', 'Tenant',
    'currentCase', 'caseAccount', 'caseContact', 'timeLogs'];
function CaseDetailController($scope, Case, HLResource, HLUtils, LocalStorage, Settings, Tenant, currentCase,
    caseAccount, caseContact, timeLogs) {
    const vm = this;
    const storage = new LocalStorage('caseDetail');

    let activeAt = true;
    if (caseContact && currentCase.account) {
        activeAt = caseContact.active_at_account[currentCase.account.id];
    }

    Settings.page.setAllTitles('detail', currentCase.subject, currentCase.contact, currentCase.account, currentCase.id,
        activeAt);
    Settings.page.toolbar.data = {
        model: 'Case',
        object: currentCase,
        field: 'subject',
        updateCallback: updateModel,
        formName: 'caseHeaderForm',
    };

    vm.case = currentCase;
    vm.case.account = caseAccount;
    vm.case.contact = caseContact;
    vm.case.timeLogs = timeLogs.objects;
    vm.mergeStreams = storage.get('mergeStreams', false);

    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.updateModel = updateModel;
    vm.toggleArchived = toggleArchived;

    activate();

    //////

    function activate() {
        Tenant.query({}, tenant => {
            vm.tenant = tenant;
        });

        vm.caseStart = moment(vm.case.created).subtract(2, 'days').format('YYYY-MM-DD');

        let caseEnd;

        if (vm.case.status.name === 'Closed') {
            caseEnd = moment(vm.case.modified);
        } else {
            caseEnd = moment();
        }

        vm.caseEnd = caseEnd.add(2, 'days').format('YYYY-MM-DD');

        Case.getStatuses(response => {
            vm.statusChoices = response.results;

            vm.closedStatus = Case.closedStatus;
        });

        // TODO: This should be some util functions.
        vm.recipients = getRecipients();
    }

    function getRecipients() {
        const {account, contact} = vm.case;

        let emailAddress = null;

        if (account && contact) {
            if (contact.email_addresses.length === 0) {
                // No personal email addresses, but account has email addresses.
                if (account.email_addresses.length > 1) {
                    // Get the email address set as primary or otherwise just the first one.
                    emailAddress = account.email_addresses.find(email => email.is_primary) || account.email_addresses[0];
                }
            } else {
                // Check if any of the contact's email addresses match any of the account's domains.
                account.websites.forEach(website => {
                    emailAddress = contact.email_addresses.find(email => email.email_address.includes(website.second_level));
                });
            }
        }

        if (!emailAddress) {
            if (contact) {
                emailAddress = contact.email_addresses.find(email => email.is_primary) || contact.email_addresses[0];
            } else if (account) {
                emailAddress = account.email_addresses.find(email => email.is_primary) || account.email_addresses[0];
            }
        }

        if (emailAddress) {
            return [{...contact, emailAddress: emailAddress.email_address}];
        }

        return [];
    }

    function updateModel(data, field) {
        const args = HLResource.createArgs(data, field, vm.case);
        const casePriorities = Case.getCasePriorities();

        if (field === 'subject') {
            Settings.page.setAllTitles('detail', data, vm.case.contact, vm.case.account, vm.case.id);
        }

        if (args.hasOwnProperty('assigned_to_teams')) {
            const oldTeams = vm.case.assigned_to_teams.map(team => ({'id': team.id}));
            const teamIds = args.assigned_to_teams.map(team => team.id);
            let removedTeams = oldTeams.filter(team => teamIds.indexOf(team.id) === -1);
            for (let team of removedTeams) team.is_deleted = true;
            args.assigned_to_teams = args.assigned_to_teams.map(team => ({'id': team.id})).concat(removedTeams);
        }

        if (args.hasOwnProperty('priority')) {
            let expireDate = HLUtils.addBusinessDays(casePriorities[vm.case.priority].date_increment);
            expireDate = moment(expireDate).format('YYYY-MM-DD');

            vm.case.expires = expireDate;
            args.expires = vm.case.expires;
        }

        return HLResource.patch('Case', args).$promise;
    }

    function changeCaseStatus(status) {
        vm.case.status = status;

        return updateModel(status.id, 'status').then(() => {
            if (status.id === vm.closedStatus.id) {
                // A 'Closed' case is automatically set to archived in the API.
                // So update in the front end as well.
                vm.case.is_archived = true;
            }
        });
    }

    function assignCase() {
        vm.case.assigned_to = currentUser;
        vm.case.assigned_to.full_name = currentUser.fullName;

        if (currentUser.teams.length) {
            vm.case.assigned_to_teams = currentUser.teams;
        }

        // Broadcast function to update model correctly after dynamically
        // changing the assignee by using the 'assign to me' link.
        $scope.$broadcast('activateEditableSelect', currentUser.id);

        return updateModel(currentUser.id, 'assigned_to');
    }

    function toggleArchived() {
        vm.case.is_archived = !vm.case.is_archived;

        updateModel(vm.case.is_archived, 'is_archived');
    }

    $scope.$watch('vm.mergeStreams', () => {
        storage.put('mergeStreams', vm.mergeStreams);
    });
}
