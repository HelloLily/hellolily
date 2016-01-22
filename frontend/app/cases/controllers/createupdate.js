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
        url: '/contact/{contactId:[0-9]{1,}}',
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
        url: '/account/{accountId:[0-9]{1,}}',
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

CaseCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Case', 'Contact', 'ContactDetail',
    'HLForms', 'HLSearch', 'HLUtils', 'Settings', 'UserTeams', 'User'];
function CaseCreateUpdateController($scope, $state, $stateParams, Account, Case, Contact, ContactDetail, HLForms,
                                    HLSearch, HLUtils, Settings, UserTeams, User) {
    var vm = this;

    vm.case = {};
    vm.teams = [];
    vm.assignOptions = [];
    vm.caseTypes = [];
    vm.caseStatuses = [];
    vm.casePriorities = [];
    vm.formPortlets = {
        0: {
            fields: [],
        },
        1: {
            fields: ['subject', 'type', 'status'],
        },
        2: {
            fields: ['priority', 'expires'],
        },
        3: {
            fields: [],
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
        vm.case.expires = HLUtils.addBusinessDays(vm.case.priority);
    });

    var watchGroup = [
        'vm.case.type',
        'vm.case.status',
        'vm.case.priority',
        'vm.case.expires',
        'vm.case.account',
        'vm.case.contact',
    ];

    $scope.$watchGroup(watchGroup, function(newValues, oldValues) {
        if (newValues !== oldValues && !vm.case.id) {
            openNextStep();
        }
    });

    function openNextStep() {
        for (var i = vm.startsAt; i < Object.keys(vm.formPortlets).length; i++) {
            var fieldHasValue = true;
            var portlet = vm.formPortlets[i];

            // Check if all fields are set.
            portlet.fields.forEach(function(field) {
                // 0 is a valid input (selects), so allow it.
                if (vm.case[field] === '' || vm.case[field] === null || vm.case[field] === undefined) {
                    fieldHasValue = false;
                }
            });

            if (!fieldHasValue) {
                // Fields not completely filled in, so just stop checking the portlets.
                break;
            }

            if (!portlet.portlet.isComplete) {
                portlet.portlet.isComplete = true;
                if (vm.formPortlets[i + 1]) {
                    vm.formPortlets[i + 1].portlet.collapsed = false;
                }

                return;
            }
        }
    }

    activate();

    ////

    function activate() {
        _getAssignOptions();
        _getTeams();

        Case.caseTypes(function(data) {
            vm.caseTypes = data;

            angular.forEach(data, function(caseType) {
                if (caseType.type.indexOf('Config') > -1) {
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
    }

    function _getCase() {
        // Fetch the contact or create empty contact.
        if ($stateParams.id) {
            Case.get({id: $stateParams.id}).$promise.then(function(lilyCase) {
                vm.case = Case.clean(lilyCase);

                Settings.page.setAllTitles('edit', lilyCase.subject);
            });
        } else {
            Settings.page.setAllTitles('create', 'case');
            vm.case = Case.create();

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}).$promise.then(function(account) {
                    vm.case.account = account;
                });
            }

            if ($stateParams.contactId) {
                Contact.get({id: $stateParams.contactId}).$promise.then(function(contact) {
                    vm.case.contact = contact;
                    // API returns 'full_name' but ES returns 'name'. So get the full name and set the name.
                    vm.case.contact.name = contact.full_name;
                });
            }

            if (Settings.email.data && (Settings.email.data.account || Settings.email.data.contact)) {
                // Auto fill data if it's available.
                if (Settings.email.data.contact.id) {
                    if (Settings.email.data && Settings.email.data.account) {
                        var filterquery = 'accounts.id:' + Settings.email.data.account.id;

                        ContactDetail.query({filterquery: filterquery}).$promise.then(function (colleagues) {
                            var colleagueIds = [];
                            angular.forEach(colleagues, function (colleague) {
                                colleagueIds.push(colleague.id);
                            });

                            // Check if the contact actually works at the account.
                            if (colleagueIds.indexOf(Settings.email.data.contact.id) > -1) {
                                vm.case.contact = Settings.email.data.contact.id;
                            }
                        });
                    } else {
                        vm.case.contact = Settings.email.data.contact.id;
                    }
                }

                if (Settings.email.data && Settings.email.data.account) {
                    vm.case.account = Settings.email.data.account.id;
                }
            }

            if (Settings.email.sidebar.form) {
                vm.startsAt = 1;
            } else {
                vm.startsAt = 0;
            }
        }
    }

    function _getAssignOptions() {
        var assignOptions = [];

        User.query().$promise.then(function(userList) {
            angular.forEach(userList, function(user) {
                if (user.first_name !== '') {
                    assignOptions.push({
                        id: user.id,
                        // Convert to single string so searching with spaces becomes possible.
                        name: HLUtils.getFullName(user),
                    });
                }
            });

            vm.assignOptions = assignOptions;
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
        if (Settings.email.sidebar.form === 'cases') {
            Settings.email.sidebar.form = null;
            Settings.email.sidebar.case = false;
        } else {
            $state.go('base.cases');
        }
    }

    function saveCase(form, archive) {
        if (!_caseFormIsValid()) {
            return false;
        }

        HLForms.blockUI();

        vm.case = Case.clean(vm.case);

        // Clear all errors of the form (in case of new errors).
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
            // If there's an ID set it means we're dealing with an existing contact, so update it.
            vm.case.$update(function() {
                toastr.success('I\'ve updated the case for you!', 'Done');
                $state.go('base.cases.detail', {id: vm.case.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            vm.case.$save(function() {
                toastr.success('I\'ve saved the case for you!', 'Yay');

                if (Settings.email.sidebar.form === 'cases') {
                    Settings.email.sidebar.form = null;

                    Metronic.unblockUI();
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

    function _caseFormIsValid() {
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
        } else if ((vm.case.assigned_to_groups && !vm.case.assigned_to_groups.length) && !vm.case.assigned_to) {
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
