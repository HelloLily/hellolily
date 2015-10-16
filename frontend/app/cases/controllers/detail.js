angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'cases/controllers/detail.html',
                controller: CaseDetailController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: '{{ case.subject }}'
        },
        resolve: {
            caseItem: ['CaseDetail', '$stateParams', function(CaseDetail, $stateParams) {
                var id = $stateParams.id;
                return CaseDetail.get({id: id}).$promise;
            }]
        }
    });
}

angular.module('app.cases').controller('CaseDetailController', CaseDetailController);

CaseDetailController.$inject = ['$http', '$modal', '$scope', '$state', '$stateParams', 'Account', 'CaseStatuses', 'caseItem', 'Contact'];
function CaseDetailController ($http, $modal, $scope, $state, $stateParams, Account, CaseStatuses, caseItem, Contact) {
    var vm = this;
    $scope.conf.pageTitleBig = 'Case';
    $scope.conf.pageTitleSmall = 'the devil is in the details';
    var id = $stateParams.id;
    vm.case = caseItem;
    vm.caseStatuses = CaseStatuses.query();

    vm.getPriorityDisplay = getPriorityDisplay;
    vm.changeCaseStatus = changeCaseStatus;
    vm.assignCase = assignCase;
    vm.archive = archive;
    vm.unarchive = unarchive;
    vm.openPostponeWidget = openPostponeWidget;

    activate();

    //////

    function activate () {
        Account.get({id: vm.case.account}).$promise.then(function (account) {
            vm.account = account;
        });

        Contact.get({id: vm.case.contact}).$promise.then(function (contact) {
            vm.contact = contact;
        });
    }

    /**
     *
     * @returns {string}: A string which states what label should be displayed
     */
    function getPriorityDisplay () {
        if (vm.case.is_archived) {
            return 'label-default';
        } else {
            switch (vm.case.priority) {
                case 0:
                    return 'label-success';
                case 1:
                    return 'label-info';
                case 2:
                    return 'label-warning';
                case 3:
                    return 'label-danger';
                default :
                    return 'label-info';
            }
        }
    }

    function changeCaseStatus (status) {
        // TODO: LILY-XXX: Temporary call to change status of a case, will be replaced with an new API call later
        var req = {
            method: 'POST',
            url: '/cases/update/status/' + vm.case.id + '/',
            data: 'status=' + status,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.status = data.status;
            }).
            error(function(data, status, headers, config) {
                // Request failed proper error?
            });
    }

    function assignCase () {
        var assignee = '';

        if (vm.case.assigned_to_id != currentUser.id) {
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
                    vm.case.assigned_to_id = data.assignee.id;
                    vm.case.assigned_to_name = data.assignee.name;
                }
                else {
                    vm.case.assigned_to_id = null;
                    vm.case.assigned_to_name = null;
                }
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Archive a deal.
     * TODO: LILY-XXX: Change to API based archiving
     */
    function archive (id) {
        var req = {
            method: 'POST',
            url: '/cases/archive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.status = data.status;
                vm.case.archived = true;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    /**
     * Unarchive a deal.
     * TODO: LILY-XXX: Change to API based unarchiving
     */
    function unarchive (id) {
        var req = {
            method: 'POST',
            url: '/cases/unarchive/',
            data: 'id=' + id,
            headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        };

        $http(req).
            success(function(data, status, headers, config) {
                vm.case.archived = false;
            }).
            error(function(data, status, headers, config) {
                // Request failed propper error?
            });
    }

    function openPostponeWidget (myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/postpone.html',
            controller: 'CasePostponeModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase
                }
            }
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}
