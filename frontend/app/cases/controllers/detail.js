angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases.detail', {
        parent: 'base.cases',
        url: '/{id:[0-9]{1,}}',
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
                    account = Account.get({id: currentCase.account.id}).$promise;
                }

                return account;
            }],
            caseContact: ['Contact', 'currentCase', function(Contact, currentCase) {
                var contact;

                if (currentCase.contact) {
                    contact = Contact.get({id: currentCase.contact.id}).$promise;
                }

                return contact;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$scope', 'Settings', 'CaseStatuses', 'HLResource', 'HLUtils', 'LocalStorage', 'Tenant',
    'UserTeams', 'currentCase', 'caseAccount', 'caseContact', 'Case'];
function CaseDetailController($scope, Settings, CaseStatuses, HLResource, HLUtils, LocalStorage, Tenant, UserTeams,
                              currentCase, caseAccount, caseContact, Case) {
    var vm = this;
    var storage = new LocalStorage('caseDetail');

    Settings.page.setAllTitles('detail', currentCase.subject, currentCase.contact, currentCase.account);
    Settings.page.toolbar.data = {
        model: 'Case',
        object: currentCase,
        field: 'subject',
        updateCallback: updateModel,
    };

    vm.case = currentCase;
    vm.case.account = caseAccount;
    vm.case.contact = caseContact;
    vm.caseStatuses = CaseStatuses.query();
    vm.mergeHistory = storage.get('mergeHistory', false);

    vm.getPriorityDisplay = getPriorityDisplay;
    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.updateModel = updateModel;

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
    }

    /**
     *
     * @returns {string}: A string which states what label should be displayed
     */
    function getPriorityDisplay() {
        var label = '';

        if (vm.case.is_archived) {
            label = 'label-default';
        } else {
            switch (vm.case.priority) {
                case 0:
                    label = 'label-success';
                    break;
                case 1:
                    label = 'label-info';
                    break;
                case 2:
                    label = 'label-warning';
                    break;
                case 3:
                    label = 'label-danger';
                    break;
                default :
                    label = 'label-info';
                    break;
            }
        }

        return label;
    }

    function updateModel(data, field) {
        var args = HLResource.createArgs(data, field, vm.case);
        var casePriorities = Case.getCasePriorities();
        var groups = [];
        var expireDate;

        if (field === 'subject') {
            Settings.page.setAllTitles('detail', data, vm.case.contact, vm.case.account);
        }

        if (args.hasOwnProperty('assigned_to_groups')) {
            args.assigned_to_groups.forEach(function(group) {
                groups.push(group.id);
            });

            args.assigned_to_groups = groups;
        }

        if (args.hasOwnProperty('priority')) {
            expireDate = HLUtils.addBusinessDays(casePriorities[vm.case.priority].dateIncrement);
            expireDate = moment(expireDate).format('YYYY-MM-DD');

            vm.case.expires = expireDate;
            args.expires = vm.case.expires;
        }

        return HLResource.patch('Case', args).$promise;
    }

    function changeCaseStatus(status) {
        vm.case.status = status;

        return updateModel(status.id, 'status');
    }

    function assignCase() {
        vm.case.assigned_to = currentUser;
        vm.case.assigned_to.full_name = currentUser.fullName;

        // Broadcast function to update model correctly after dynamically
        // changing the assignee by using the 'assign to me' link.
        $scope.$broadcast('activateEditableSelect', currentUser.id);

        return updateModel(currentUser.id, 'assigned_to');
    }

    $scope.$watch('vm.case.is_archived', function(newValue, oldValue) {
        if (newValue !== oldValue) {
            updateModel(vm.case.is_archived, 'is_archived');
        }
    });

    $scope.$watch('vm.mergeHistory', function() {
        storage.put('mergeHistory', vm.mergeHistory);
    });
}
