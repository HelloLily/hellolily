angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases.detail', {
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
            caseItem: ['Case', '$stateParams', function(Case, $stateParams) {
                var id = $stateParams.id;
                return Case.get({id: id}).$promise;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$http', '$scope', 'Settings', 'Account', 'CaseStatuses', 'caseItem', 'Contact',
    'UserTeams', 'HLResource', 'Tenant'];
function CaseDetailController($http, $scope, Settings, Account, CaseStatuses, caseItem, Contact,
                              UserTeams, HLResource, Tenant) {
    var vm = this;

    Settings.page.setAllTitles('detail', caseItem.subject);

    vm.case = caseItem;
    vm.caseStatuses = CaseStatuses.query();

    vm.getPriorityDisplay = getPriorityDisplay;
    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.updateModel = updateModel;

    activate();

    //////

    function activate() {
        var assignedToGroups = [];
        var caseEnd;

        if (vm.case.account) {
            Account.get({id: vm.case.account.id}).$promise.then(function(account) {
                vm.account = account;
            });
        }

        if (vm.case.contact) {
            Contact.get({id: vm.case.contact.id}).$promise.then(function(contact) {
                vm.contact = contact;
            });
        }

        angular.forEach(vm.case.assigned_to_groups, function(response) {
            UserTeams.get({id: response.id}).$promise.then(function(team) {
                assignedToGroups.push(team);
            });
        });

        Tenant.query({}, function(tenant) {
            vm.tenant = tenant;
        });

        vm.case.assigned_to_groups = assignedToGroups;

        vm.caseStart = moment(vm.case.created).subtract(2, 'days').format('YYYY-MM-DD');

        if (vm.case.status.status === 'Closed') {
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
        var args;

        if (typeof data === 'object') {
            args = data;
        } else {
            args = {
                id: vm.case.id,
            };

            args[field] = data;

            if (field === 'name') {
                Settings.page.setAllTitles('detail', data);
            }
        }

        return HLResource.patch('Case', args).$promise;
    }

    function changeCaseStatus(status) {
        // TODO: LILY-XXX: Temporary call to change status of a case, will be replaced with an new API call later
        var req = {
            method: 'POST',
            url: '/cases/update/status/' + vm.case.id + '/',
            data: 'status=' + status,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.status.status = data.status;
            }).
            error(function(data, status, headers, config) {
                // Request failed proper error?
            });
    }

    function assignCase() {
        var assignee = '';

        if (vm.case.assigned_to_id !== currentUser.id) {
            assignee = currentUser.id;
        }

        var req = {
            method: 'POST',
            url: '/cases/update/assigned_to/' + vm.case.id + '/',
            data: 'assignee=' + assignee,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                if (data.assignee) {
                    vm.case.assigned_to = data.assignee;
                    vm.case.assigned_to.id = data.assignee.id;
                    vm.case.assigned_to.full_name = data.assignee.name;
                    // Broadcast function to update model correctly after dynamically
                    // changing the assignee by using the 'assign to me' link.
                    $scope.$broadcast('activateEditableSelect', data.assignee.id);
                } else {
                    vm.case.assigned_to_id = null;
                    vm.case.assigned_to_name = null;
                }

                $scope.loadNotifications();
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    $scope.$watch('vm.case.is_archived', function(newValue, oldValue) {
        if (newValue !== oldValue) {
            updateModel(vm.case.is_archived, 'is_archived');
        }
    });
}
