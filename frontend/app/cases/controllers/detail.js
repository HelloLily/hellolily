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
            currentCase: ['Case', '$stateParams', function(Case, $stateParams) {
                var id = $stateParams.id;
                return Case.get({id: id}).$promise;
            }],
            caseAccount: ['Account', 'currentCase', function(Account, currentCase) {
                var account;

                if (currentCase.account) {
                    account = Account.get({id: currentCase.account.id, filter_deleted: 'False'}).$promise;
                }

                return account;
            }],
            caseContact: ['Contact', 'currentCase', function(Contact, currentCase) {
                var contact;

                if (currentCase.contact) {
                    contact = Contact.get({id: currentCase.contact.id, filter_deleted: 'False'}).$promise;
                }

                return contact;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$scope', 'Case', 'HLResource', 'HLUtils', 'LocalStorage', 'Settings', 'Tenant',
    'currentCase', 'caseAccount', 'caseContact', 'Case'];
function CaseDetailController($scope, Case, HLResource, HLUtils, LocalStorage, Settings, Tenant, currentCase,
    caseAccount, caseContact) {
    var vm = this;
    var storage = new LocalStorage('caseDetail');

    var activeAt = true;
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
    vm.mergeStreams = storage.get('mergeStreams', false);

    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.updateModel = updateModel;
    vm.toggleArchived = toggleArchived;

    activate();

    //////

    function activate() {
        var caseEnd;

        Tenant.query({}, function(tenant) {
            vm.tenant = tenant;
        });

        vm.caseStart = moment(vm.case.created).subtract(2, 'days').format('YYYY-MM-DD');

        if (vm.case.status.name === 'Closed') {
            caseEnd = moment(vm.case.modified);
        } else {
            caseEnd = moment();
        }

        vm.caseEnd = caseEnd.add(2, 'days').format('YYYY-MM-DD');

        Case.getStatuses(function(response) {
            vm.statusChoices = response.results;

            vm.closedStatus = Case.closedStatus;
        });
    }

    function updateModel(data, field) {
        var args = HLResource.createArgs(data, field, vm.case);
        var casePriorities = Case.getCasePriorities();
        var expireDate;

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
            expireDate = HLUtils.addBusinessDays(casePriorities[vm.case.priority].date_increment);
            expireDate = moment(expireDate).format('YYYY-MM-DD');

            vm.case.expires = expireDate;
            args.expires = vm.case.expires;
        }

        return HLResource.patch('Case', args).$promise;
    }

    function changeCaseStatus(status) {
        vm.case.status = status;

        return updateModel(status.id, 'status').then(function() {
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

        // Broadcast function to update model correctly after dynamically
        // changing the assignee by using the 'assign to me' link.
        $scope.$broadcast('activateEditableSelect', currentUser.id);

        return updateModel(currentUser.id, 'assigned_to');
    }

    function toggleArchived() {
        vm.case.is_archived = !vm.case.is_archived;

        updateModel(vm.case.is_archived, 'is_archived');
    }

    $scope.$watch('vm.mergeStreams', function() {
        storage.put('mergeStreams', vm.mergeStreams);
    });
}
