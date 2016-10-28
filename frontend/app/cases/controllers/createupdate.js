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
        resolve: {
            currentCase: function() {
                return null;
            },
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
        resolve: {
            currentCase: function() {
                return null;
            },
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
        resolve: {
            currentCase: function() {
                return null;
            },
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
        resolve: {
            currentCase: ['Case', '$stateParams', function(Case, $stateParams) {
                var id = $stateParams.id;
                return Case.get({id: id}).$promise;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseCreateUpdateController', CaseCreateUpdateController);

CaseCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Case', 'Contact', 'HLForms',
    'HLSearch', 'HLUtils', 'Settings', 'UserTeams', 'User', 'currentCase'];
function CaseCreateUpdateController($scope, $state, $stateParams, Account, Case, Contact, HLForms,
                                    HLSearch, HLUtils, Settings, UserTeams, User, currentCase) {
    var vm = this;

    vm.case = {};
    vm.teams = [];
    vm.caseTypes = [];
    vm.caseStatuses = [];
    vm.casePriorities = [];
    vm.datepickerOptions = {
        startingDay: 1,
    };
    vm.configCaseType = 0;

    vm.assignToMe = assignToMe;
    vm.assignToMyTeams = assignToMyTeams;
    vm.cancelCaseCreation = cancelCaseCreation;
    vm.saveCase = saveCase;
    vm.refreshAccounts = refreshAccounts;
    vm.refreshContacts = refreshContacts;
    vm.refreshUsers = refreshUsers;

    activate();

    ////

    function activate() {
        _getTeams();

        Case.getCaseTypes(function(data) {
            vm.caseTypes = data;

            angular.forEach(data, function(caseType) {
                if (caseType.name.indexOf('Config') > -1) {
                    vm.configCaseType = caseType.id;
                }
            });
        });

        Case.caseStatuses(function(data) {
            vm.caseStatuses = data;

            vm.case.status = vm.caseStatuses[0];
        });

        vm.casePriorities = Case.getCasePriorities();

        //TODO: This should be an API call.
        vm.parcelProviders = [
            {id: 1, name: 'DPD'},
        ];

        _getCase();
    }

    function _getCase() {
        var filterquery = '';
        var i;

        // Fetch the case or create an empty one.
        if (currentCase) {
            vm.case = currentCase;

            Settings.page.setAllTitles('edit', currentCase.subject);
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

                    if (vm.case.contact.accounts && vm.case.contact.accounts.length === 1) {
                        // Automatically fill in the account the contact works at.
                        vm.case.account = vm.case.contact.accounts[0];
                    }
                });
            }

            if (Settings.email.data && (Settings.email.data.account || Settings.email.data.contact)) {
                // Auto fill data if it's available.
                if (Settings.email.data.contact && Settings.email.data.contact.id) {
                    if (Settings.email.data && Settings.email.data.account) {
                        // Check if the contact actually works at the account.
                        filterquery = 'accounts.id:' + Settings.email.data.account.id;

                        Contact.search({filterquery: filterquery}).$promise.then(function(colleagues) {
                            for (i = 0; i < colleagues.objects.length; i++) {
                                if (colleagues.objects[i].id === Settings.email.data.contact.id) {
                                    vm.case.contact = Settings.email.data.contact.id;
                                }
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

    $scope.$watch('vm.case.priority', function() {
        if (vm.case.expires) {
            vm.case.expires = HLUtils.addBusinessDays(vm.casePriorities[vm.case.priority].dateIncrement);
        }
    });

    function _getTeams() {
        UserTeams.query().$promise.then(function(response) {
            vm.teams = response.results;
        });

        UserTeams.mine(function(teams) {
            vm.ownTeams = teams;
        });
    }

    function assignToMe() {
        // Bit of a hacky way to assign the current user, but we'll clean this up later.
        vm.case.assigned_to = {id: currentUser.id, full_name: currentUser.fullName};
    }

    function assignToMyTeams() {
        vm.case.assigned_to_teams = vm.ownTeams;
    }

    function cancelCaseCreation() {
        if (Settings.email.sidebar.form === 'cases') {
            Settings.email.sidebar.form = null;
            Settings.email.sidebar.case = false;
        } else {
            if (Settings.page.previousState && !Settings.page.previousState.state.abstract) {
                // Check if we're coming from another page.
                $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
            } else {
                $state.go('base.cases');
            }
        }
    }

    function saveCase(form, archive) {
        var cleanedCase;

        // Check if a case is being saved (and archived) via the + case page
        // or via a supercard.
        if (Settings.email.sidebar.isVisible && archive) {
            ga('send', 'event', 'Case', 'Save and archive', 'Email Sidebar');
        } else if (Settings.email.sidebar.isVisible && !archive) {
            ga('send', 'event', 'Case', 'Save', 'Email Sidebar');
        } else if (!Settings.email.sidebar.isVisible && archive) {
            if ($stateParams.accountId) {
                ga('send', 'event', 'Case', 'Save and archive', 'Account Widget');
            } else if ($stateParams.contactId) {
                ga('send', 'event', 'Case', 'Save and archive', 'Contact Widget');
            } else {
                ga('send', 'event', 'Case', 'Save and archive', 'Default');
            }
        } else {
            if ($stateParams.accountId) {
                ga('send', 'event', 'Case', 'Save', 'Account Widget');
            } else if ($stateParams.contactId) {
                ga('send', 'event', 'Case', 'Save', 'Contact Widget');
            } else {
                ga('send', 'event', 'Case', 'Save', 'Default');
            }
        }

        if (!_caseFormIsValid()) {
            return;
        }

        HLForms.blockUI();

        if (vm.case.id) {
            // TODO: Hopefully temporary fix to allow clearing these fields.
            // Because the API doesn't see missing fields as cleared.
            if (!vm.case.account) {
                vm.case.account = null;
            }

            if (!vm.case.contact) {
                vm.case.contact = null;
            }

            if (!vm.case.assigned_to) {
                vm.case.assigned_to = null;
            }
        }

        HLForms.clearErrors(form);

        if (archive) {
            vm.case.is_archived = true;
        }

        vm.case.expires = moment(vm.case.expires).format('YYYY-MM-DD');

        // Clean modifies the object, so preserve the state by copying the object (in case of errors).
        cleanedCase = HLForms.clean(angular.copy(vm.case));

        if (cleanedCase.id) {
            // If there's an ID set it means we're dealing with an existing contact, so update it.
            cleanedCase.$update(function() {
                new Intercom('trackEvent', 'case-created');

                toastr.success('I\'ve updated the case for you!', 'Done');
                $state.go('base.cases.detail', {id: cleanedCase.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            cleanedCase.$save(function() {
                toastr.success('I\'ve saved the case for you!', 'Yay');

                if (Settings.email.sidebar.form === 'cases') {
                    Settings.email.sidebar.form = null;

                    Metronic.unblockUI();
                } else {
                    $state.go('base.cases.detail', {id: cleanedCase.id});
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

    $scope.$watch('vm.case.contact', function() {
        if (vm.case.contact && vm.case.contact.accounts && vm.case.contact.accounts.length) {
            // Get accounts that the select contact works for.
            vm.accounts = vm.case.contact.accounts;
        } else {
            // Just get the accounts list.
            vm.accounts = null;
            refreshAccounts('');
        }
    });

    function refreshAccounts(query) {
        var accountsPromise;

        // Don't load if we selected a contact.
        // Because we want to display all accounts the contact works for.
        if (!vm.case.contact && (!vm.accounts || query.length)) {
            accountsPromise = HLSearch.refreshList(query, 'Account');

            if (accountsPromise) {
                accountsPromise.$promise.then(function(data) {
                    vm.accounts = data.objects;
                });
            }
        }
    }

    function refreshContacts(query) {
        var accountQuery = '';
        var contactsPromise;

        if (vm.case.account) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show contacts of the selected account.
            accountQuery += 'accounts.id:' + vm.case.account.id;
        }

        contactsPromise = HLSearch.refreshList(query, 'Contact', accountQuery, '', 'full_name');

        if (contactsPromise) {
            contactsPromise.$promise.then(function(data) {
                vm.contacts = data.objects;
                if (vm.contacts.length === 1) {
                    vm.case.contact = vm.contacts[0];
                }
            });
        }
    }

    function refreshUsers(query) {
        var usersPromise;

        if (!vm.assigned_to && (!vm.users || query.length)) {
            usersPromise = HLSearch.refreshList(query, 'User', '', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(function(data) {
                    vm.users = data.objects;
                });
            }
        }
    }

    function _caseFormIsValid() {
        if (!vm.case.account && !vm.case.contact) {
            swal({
                title: 'No account or contact',
                text: 'Please select an account or contact the case belongs to',
                type: 'warning',
                confirmButtonText: 'Let me fix that for you',
                confirmButtonClass: 'btn btn-success',
            }).done();

            return false;
        } else if ((vm.case.assigned_to_teams && !vm.case.assigned_to_teams.length) && !vm.case.assigned_to) {
            swal({
                title: 'No assignee set',
                text: 'Please select a colleague or team to assign the case to',
                type: 'warning',
                confirmButtonText: 'Let me fix that for you',
                confirmButtonClass: 'btn btn-success',
            }).done();

            return false;
        }

        return true;
    }

    $scope.$on('saveCase', function() {
        saveCase($scope.caseForm);
    });
}
