angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'cases/controllers/form.html',
                controller: CaseCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
    });

    $stateProvider.state('base.cases.create.fromContact', {
        url: '/contact/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'cases/controllers/form.html',
                controller: CaseCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            skip: true,
        },
    });

    $stateProvider.state('base.cases.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'cases/controllers/form.html',
                controller: CaseCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            skip: true,
        },
    });

    $stateProvider.state('base.cases.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'cases/controllers/form.html',
                controller: CaseCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit',
        },
    });
}

angular.module('app.cases').controller('CaseCreateUpdateController', CaseCreateUpdateController);

CaseCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Case', 'Contact', 'HLForms',
                                      'HLSearch', 'HLUtils', 'Settings', 'UserTeams', 'User'];
function CaseCreateUpdateController($scope, $state, $stateParams, Account, Case, Contact, HLForms, HLSearch, HLUtils,
                                    Settings, UserTeams, User) {
    var vm = this;

    vm.case = {};
    vm.teams = [];
    vm.people = [];
    vm.caseTypes = [];
    vm.caseStatuses = [];
    vm.casePriorities = [];
    vm.formPortlets = {
        0: {
            fields: ['subject', 'type'],
        },
        1: {
            fields: ['status', 'priority', 'expires'],
        },
        2: {
            fields: [''],
        },
    };
    vm.datepickerOptions = {
        startingDay: 1,
    };
    vm.configCaseType = 0;

    vm.assignToMe = assignToMe;
    vm.cancelCaseCreation = cancelCaseCreation;
    vm.saveCase = saveCase;
    vm.openNextStep = openNextStep;
    vm.refreshAccounts = refreshAccounts;
    vm.refreshContacts = refreshContacts;

    $scope.$watch('vm.case.priority', function() {
        var daysToAdd = [5, 3, 1, 0];

        var i = 0;
        var newDate = moment();

        // Add days based on what the priority is. Skip weekends.
        while (i < daysToAdd[vm.case.priority]) {
            newDate = newDate.add(1, 'day');

            if (newDate.day() !== 0 && newDate.day() !== 6) {
                i++;
            }
        }

        vm.case.expires = newDate.format();
    });

    $scope.$watchGroup(['vm.case.type', 'vm.case.status', 'vm.case.priority', 'vm.case.expires'], function() {
        openNextStep();
    });

    function openNextStep() {
        for (var i = 0; i < Object.keys(vm.formPortlets).length; i++) {
            var fieldsSet = true;
            var portlet = vm.formPortlets[i];

            // Check if all fields are set.
            portlet.fields.forEach(function(field) {
                // 0 is a valid input (selects), so allow it.
                if (vm.case[field] === '' || vm.case[field] === null || vm.case[field] === undefined) {
                    fieldsSet = false;
                }
            });

            if (!fieldsSet) {
                // Fields not completely filled in, so just stop checking the portlets.
                break;
            }

            // Automatically close the current portlet if it hasn't been completed.
            if (!portlet.portlet.collapsed && !portlet.portlet.isComplete) {
                portlet.portlet.isComplete = true;
                vm.formPortlets[i + 1].portlet.collapsed = false;

                return;
            }
        }
    }

    activate();

    ////

    function activate() {
        _getPeople();
        _getTeams();

        Case.caseTypes(function(data) {
            vm.caseTypes = data;

            angular.forEach(data, function(caseType) {
                if (caseType.type === 'Config') {
                    vm.configCaseType = caseType.id;
                }
            });
        });

        Case.caseStatuses(function(data) {
            vm.caseStatuses = data;
        });

        vm.casePriorities = Case.casePriorities;

        //TODO: This should be an API call.
        vm.parcelProviders = [
            {id: 1, name: 'DPD'},
        ];

        _getCase();

        //vm.accounts = Account.search({size: 60, sort: '-modified'});
        //vm.contacts = Contact.search({size: 60, sort: '-modified'});
    }

    function _getCase() {
        // Fetch the contact or create empty contact
        if ($stateParams.id) {
            Case.get({id: $stateParams.id}).$promise.then(function(lilyCase) {
                vm.case = lilyCase;
                Settings.page.setAllTitles('edit', lilyCase.subject);
            });
        } else {
            Settings.page.setAllTitles('create', 'case');
            vm.case = Case.create();

            if ($scope.emailSettings) {
                // Auto fill data if it's available
                if ($scope.emailSettings.contact) {
                    vm.case.contact = $scope.emailSettings.contact;
                }

                if ($scope.emailSettings.account) {
                    vm.case.account = $scope.emailSettings.account;
                }
            }
        }
    }

    function _getPeople() {
        User.query().$promise.then(function(userList) {
            angular.forEach(userList, function(user) {
                if (user.first_name !== '') {
                    vm.people.push({
                        id: user.id,
                        // Convert to single string so searching with spaces becomes possible
                        name: HLUtils.getFullName(user),
                    });
                }
            });
        });
    }

    function _getTeams() {
        UserTeams.query().$promise.then(function(teams) {
            vm.teams = teams;
        });
    }

    function assignToMe() {
        vm.case.assigned_to = currentUser.id;
    }

    function cancelCaseCreation() {
        if ($scope.emailSettings.sidebar.form === 'createCase') {
            $scope.emailSettings.sidebar.form = null;
            $scope.emailSettings.sidebar.case = false;
        } else {
            $state.go('base.cases');
        }
    }

    function saveCase(form, archive) {
        if (!_checkCaseForm()) {
            return false;
        }

        HLForms.blockUI();

        // Clear all errors of the form (in case of new errors)
        angular.forEach(form, function(value, key) {
            if (typeof value === 'object' && value.hasOwnProperty('$modelValue')) {
                form[key].$error = {};
                form[key].$setValidity(key, true);
            }
        });

        if (archive) {
            vm.case.is_archived = true;
        }

        vm.case.expires = moment(vm.case.expires).format('YYYY-MM-DD');

        if (vm.case.id) {
            // If there's an ID set it means we're dealing with an existing contact, so update it
            vm.case.$update(function() {
                toastr.success('I\'ve updated the case for you!', 'Done');
                $state.go('base.cases.detail', {id: vm.case.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            vm.case.$save(function() {
                toastr.success('I\'ve saved the case for you!', 'Yay');

                if ($scope.emailSettings.sidebar.form === 'createCase') {
                    $scope.emailSettings.sidebar.form = null;
                    $scope.emailSettings.sidebar.case = true;
                    $scope.emailSettings.caseId = vm.case.id;
                } else {
                    $state.go('base.cases.detail', {id: vm.case.id});
                }
            }, function(response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    $scope.$watch('vm.case.account', function() {
        // Get contacts that work for the selected account.
        refreshContacts('');
    });

    function refreshAccounts(query) {
        vm.accounts = HLSearch.refreshList(query, 'Account');
    }

    function refreshContacts(query) {
        var accountQuery = '';

        if (vm.case.account) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show contacts of the selected account.
            accountQuery += 'accounts.id:' + vm.case.account;
        }

        vm.contacts = HLSearch.refreshList(query, 'Contact', null, accountQuery);
    }

    function _checkCaseForm() {
        if (!vm.case.account && !vm.case.contact) {
            bootbox.dialog({
                message: 'Please select an account or contact the case belongs to',
                title: 'No account or contact',
                buttons: {
                    success: {
                        label: 'Let me fix that for you',
                        className: 'btn-success',
                    },
                },
            });

            return false;
        } else if (!vm.case.assigned_to_groups.length && !vm.case.assigned_to) {
            bootbox.dialog({
                message: 'Please select a colleague or team to assign the case to',
                title: 'No assignee set',
                buttons: {
                    success: {
                        label: 'Let me fix that for you',
                        className: 'btn-success',
                    },
                },
            });

            return false;
        }

        return true;
    }
}
