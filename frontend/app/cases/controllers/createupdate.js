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
            teams: ['UserTeams', function(UserTeams) {
                return UserTeams.query().$promise;
            }],
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
            teams: ['UserTeams', function(UserTeams) {
                return UserTeams.query().$promise;
            }],
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
            teams: ['UserTeams', function(UserTeams) {
                return UserTeams.query().$promise;
            }],
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
            teams: ['UserTeams', function(UserTeams) {
                return UserTeams.query().$promise;
            }],
        },
    });
}

angular.module('app.cases').controller('CaseCreateUpdateController', CaseCreateUpdateController);

CaseCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Case', 'Contact', 'HLForms',
    'HLSearch', 'HLUtils', 'Settings', 'UserTeams', 'User', 'currentCase', 'teams'];
function CaseCreateUpdateController($scope, $state, $stateParams, Account, Case, Contact, HLForms,
    HLSearch, HLUtils, Settings, UserTeams, User, currentCase, teams) {
    var vm = this;

    vm.case = {};
    vm.teams = teams.results;
    vm.caseTypes = [];
    vm.casePriorities = [];
    vm.datepickerOptions = {
        startingDay: 1,
    };
    vm.configCaseType = 0;
    vm.showSuggestions = true;

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

        User.me().$promise.then(user => {
            vm.currentUser = user;

            Case.getCaseTypes(response => {
                vm.caseTypes = response.results;

                response.results.forEach(caseType => {
                    if (caseType.name.indexOf('Config') > -1) {
                        vm.configCaseType = caseType.id;
                    }
                });
            });

            Case.getStatuses(response => {
                vm.statusChoices = response.results;

                if (!currentCase) {
                    vm.case.status = vm.statusChoices[0];
                }
            });

            vm.casePriorities = Case.getCasePriorities();

            //TODO: This should be an API call.
            vm.parcelProviders = [
                {id: 1, name: 'DPD'},
            ];

            _getCase();
        });
    }

    function _getCase() {
        // Fetch the case or create an empty one.
        if (currentCase) {
            if (currentCase.account && currentCase.account.is_deleted) {
                currentCase.account = null;
            }

            if (currentCase.contact && currentCase.contact.is_deleted) {
                currentCase.contact = null;
            }

            vm.case = currentCase;

            Settings.page.setAllTitles('edit', currentCase.subject);
        } else {
            Settings.page.setAllTitles('create', 'case');
            vm.case = Case.create();
            vm.case.assigned_to = vm.currentUser;
            vm.case.assigned_to_teams = vm.ownTeams;

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}).$promise.then(account => {
                    vm.case.account = account;
                });
            }

            if ($stateParams.contactId) {
                Contact.get({id: $stateParams.contactId}).$promise.then(contact => {
                    vm.case.contact = contact;

                    if (vm.case.contact.accounts && vm.case.contact.accounts.length === 1) {
                        // Automatically fill in the account the contact works at.
                        vm.case.account = vm.case.contact.accounts[0];
                    }
                });
            }

            if (Settings.email.data) {
                // Only prefill the case description with e-mail data if the sidebar is active.
                if (Settings.email.sidebar.isVisible) {
                    vm.case.description = $state.href('base.email.detail', {id: Settings.email.data.id}, {absolute: true});
                }

                if (Settings.email.data.account || Settings.email.data.contact) {
                    // Auto fill data if it's available.
                    if (Settings.email.data.contact && Settings.email.data.contact.id) {
                        if (Settings.email.data && Settings.email.data.account) {
                            // Check if the contact actually works at the account.
                            const filterquery = 'accounts.id:' + Settings.email.data.account.id;

                            Contact.search({filterquery}).$promise.then(colleagues => {
                                for (let i = 0; i < colleagues.objects.length; i++) {
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
            }
        }

        vm.case.expires = moment(vm.case.expires).toDate();
    }

    $scope.$watch('vm.case.priority', (newValue, oldValue) => {
        // Only change the expiry date when the priority actually gets changed.
        // So don't change if we're just loading the case.
        if ((vm.case && vm.case.id && oldValue && newValue !== oldValue) || (!vm.case.id && newValue !== oldValue)) {
            if (!vm.case.expires) {
                vm.case.expires = moment();
            }

            vm.case.expires = HLUtils.addBusinessDays(vm.casePriorities[vm.case.priority].date_increment);
        }
    });

    function _getTeams() {
        UserTeams.mine(function(myTeams) {
            vm.ownTeams = myTeams;
        });
    }

    function assignToMe() {
        vm.case.assigned_to = vm.currentUser;
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

        // Clean modifies the object, so preserve the state by copying the object (in case of errors).
        cleanedCase = HLForms.clean(angular.copy(vm.case));
        cleanedCase.expires = moment(cleanedCase.expires).format('YYYY-MM-DD');

        if (cleanedCase.id) {
            // If there's an ID set it means we're dealing with an existing case, so update it.
            cleanedCase.$update(function() {
                toastr.success('I\'ve updated the case for you!', 'Done');
                $state.go('base.cases.detail', {id: cleanedCase.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            // Save the new case.
            cleanedCase.$save(function() {
                // Track newly created cases in Intercom.
                new Intercom('trackEvent', 'case-created');

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

    $scope.$watch('vm.case.account', (newValue, oldValue) => {
        // Get contacts that work for the selected account.
        refreshContacts('');

        if (newValue !== oldValue) {
            _getOpenCases();
        }
    });

    $scope.$watch('vm.case.contact', (newValue, oldValue) => {
        if (vm.case.contact && vm.case.contact.accounts && vm.case.contact.accounts.length) {
            // Get accounts that the select contact works for.
            vm.accounts = vm.case.contact.accounts;
        } else {
            // Just get the accounts list.
            vm.accounts = null;
            refreshAccounts('');
        }

        if (newValue !== oldValue) {
            _getOpenCases();
        }
    });

    $scope.$watch('vm.case.assigned_to', (newValue, oldValue) => {
        if (vm.case.assigned_to && oldValue && newValue !== oldValue) {
            let assignToTeams = [];

            for (let team of vm.teams) {
                if (vm.case.assigned_to.teams && vm.case.assigned_to.teams.indexOf(team.id) > -1) {
                    assignToTeams.push(team);
                }
            }

            vm.case.assigned_to_teams = assignToTeams;
        }
    });

    function refreshAccounts(query) {
        // Don't load if we selected a contact.
        // Because we want to display all accounts the contact works for.
        if (!vm.case.contact || query.length) {
            const accountsPromise = HLSearch.refreshList(query, 'Account');

            if (accountsPromise) {
                accountsPromise.$promise.then(data => {
                    vm.accounts = data.objects;
                });
            }
        }
    }

    function _getOpenCases() {
        if (vm.case.account || vm.case.contact) {
            const filterQuery = `NOT status.id: ${Case.closedStatus.id} AND is_archived: false`;

            HLSearch.getOpenCasesDeals(filterQuery, vm.case, 'Case').then(response => {
                vm.openCases = response.objects;
                vm.showSuggestions = true;
            });
        } else {
            vm.openCases = [];
        }
    }

    function refreshContacts(query) {
        let accountQuery = '';

        if (vm.case.account && vm.case.account.id) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show active contacts of the selected account.
            accountQuery += 'active_at:' + vm.case.account.id;
        }

        const contactsPromise = HLSearch.refreshList(query, 'Contact', accountQuery, '', 'full_name');

        if (contactsPromise) {
            contactsPromise.$promise.then(data => {
                vm.contacts = data.objects;
                if (vm.contacts.length === 1) {
                    vm.case.contact = vm.contacts[0];
                }
            });
        }
    }

    function refreshUsers(query) {
        var usersPromise;

        if (!vm.assigned_to || query.length) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(data => {
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
            }).done();

            return false;
        } else if ((vm.case.assigned_to_teams && !vm.case.assigned_to_teams.length) && !vm.case.assigned_to) {
            swal({
                title: 'No assignee set',
                text: 'Please select a colleague or team to assign the case to',
                type: 'warning',
                confirmButtonText: 'Let me fix that for you',
            }).done();

            return false;
        }

        return true;
    }

    $scope.$on('saveCase', function() {
        saveCase($scope.caseForm);
    });
}
