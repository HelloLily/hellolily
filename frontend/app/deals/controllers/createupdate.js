angular.module('app.deals').config(dealConfig);

dealConfig.$inject = ['$stateProvider'];
function dealConfig($stateProvider) {
    $stateProvider.state('base.deals.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'deals/controllers/form.html',
                controller: DealCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
        resolve: {
            currentDeal: () => null,
            teams: ['UserTeams', UserTeams => UserTeams.query().$promise],
        },
    });

    $stateProvider.state('base.deals.create.fromAccount', {
        url: '/account/{accountId:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/form.html',
                controller: DealCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            skip: true,
        },
        resolve: {
            currentDeal: () => null,
            teams: ['UserTeams', UserTeams => UserTeams.query().$promise],
        },
    });

    $stateProvider.state('base.deals.create.fromContact', {
        url: '/contact/{contactId:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/form.html',
                controller: DealCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            skip: true,
        },
        resolve: {
            currentDeal: () => null,
            teams: ['UserTeams', UserTeams => UserTeams.query().$promise],
        },
    });

    $stateProvider.state('base.deals.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'deals/controllers/form.html',
                controller: DealCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit',
        },
        resolve: {
            currentDeal: ['Deal', '$stateParams', (Deal, $stateParams) => Deal.get({id: $stateParams.id}).$promise],
            teams: ['UserTeams', UserTeams => UserTeams.query().$promise],
        },
    });
}

angular.module('app.deals').controller('DealCreateUpdateController', DealCreateUpdateController);

DealCreateUpdateController.$inject = ['$filter', '$scope', '$state', '$stateParams', 'Account', 'Contact', 'Deal',
    'HLForms', 'HLSearch', 'HLUtils', 'Settings', 'Tenant', 'User', 'UserTeams', 'currentDeal', 'teams'];
function DealCreateUpdateController($filter, $scope, $state, $stateParams, Account, Contact, Deal, HLForms,
    HLSearch, HLUtils, Settings, Tenant, User, UserTeams, currentDeal, teams) {
    var vm = this;

    vm.deal = {};
    vm.datepickerOptions = {
        startingDay: 1,
    };
    vm.configDealType = 0;
    vm.teams = teams.results;
    vm.showSuggestions = true;

    vm.assignToMe = assignToMe;
    vm.assignToMyTeams = assignToMyTeams;
    vm.cancelDealCreation = cancelDealCreation;
    vm.saveDeal = saveDeal;
    vm.refreshAccounts = refreshAccounts;
    vm.refreshContacts = refreshContacts;
    vm.refreshUsers = refreshUsers;

    activate();

    ////

    function activate() {
        _getTeams();

        User.me().$promise.then(user => {
            vm.currentUser = user;

            Deal.getNextSteps(response => {
                vm.nextSteps = response.results;

                response.results.forEach(nextStep => {
                    if (nextStep.name === 'None') {
                        vm.noneStep = nextStep;
                    }
                });
            });

            Deal.getWhyCustomer(response => {
                vm.whyCustomer = response.results;
            });

            Deal.getWhyLost(response => {
                vm.whyLost = response.results;
            });

            Deal.getFoundThrough(response => {
                vm.foundThroughChoices = response.results;
            });

            Deal.getContactedBy(response => {
                vm.contactedByChoices = response.results;
            });

            Deal.getStatuses(response => {
                vm.statusChoices = response.results;

                vm.lostStatus = Deal.lostStatus;
                vm.wonStatus = Deal.wonStatus;
            });

            Deal.getFormOptions(data => {
                const choiceFields = ['currency'];
                const choiceData = data.actions.POST;

                for (let i = 0; i < choiceFields.length; i++) {
                    const splitName = choiceFields[i].split('_');
                    let choiceVarName = splitName[0];

                    // Convert to camelCase.
                    if (splitName.length > 1) {
                        for (let j = 1; j < splitName.length; j++) {
                            choiceVarName += splitName[j].charAt(0).toUpperCase() + splitName[j].slice(1);
                        }
                    }

                    // Make the variable name a bit more logical (e.g. vm.currencyChoices vs vm.currency).
                    choiceVarName += 'Choices';

                    vm[choiceVarName] = choiceData[choiceFields[i]].choices;
                }
            });

            // Regex to determine if the given amount is valid.
            vm.currencyRegex = /^[0-9]{1,3}(?:[0-9]*(?:[.,][0-9]{2})?|(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|(?:\.[0-9]{3})*(?:,[0-9]{1,2})?)$/;

            Tenant.query({}, tenant => {
                vm.tenant = tenant;

                if (tenant.currency) {
                    vm.deal.currency = tenant.currency;
                }
            });

            _getDeal();
        });
    }

    function _getDeal() {
        // Fetch the contact or create empty contact.
        if (currentDeal) {
            if (currentDeal.account && currentDeal.account.is_deleted) {
                currentDeal.account = null;
            }

            if (currentDeal.contact && currentDeal.contact.is_deleted) {
                currentDeal.contact = null;
            }

            vm.deal = currentDeal;

            vm.deal.amount_once = $filter('currency')(vm.deal.amount_once, '');
            vm.deal.amount_recurring = $filter('currency')(vm.deal.amount_recurring, '');

            Settings.page.setAllTitles('edit', currentDeal.name);
        } else {
            Settings.page.setAllTitles('create', 'deal');
            vm.deal = Deal.create();
            vm.deal.assigned_to = vm.currentUser;
            vm.deal.assigned_to_teams = vm.ownTeams;
            // Set new business on default when creating a deal.
            vm.deal.new_business = true;

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}).$promise.then(account => {
                    vm.deal.account = account;
                });
            }

            if ($stateParams.contactId) {
                Contact.get({id: $stateParams.contactId}).$promise.then(contact => {
                    vm.deal.contact = contact;

                    if (vm.deal.contact.accounts && vm.deal.contact.accounts.length === 1) {
                        // Automatically fill in the account the contact works at.
                        vm.deal.account = vm.deal.contact.accounts[0];
                    }
                });
            }

            if (Settings.email.data) {
                if (Settings.email.data.id) {
                    vm.deal.description = $state.href('base.email.detail', {id: Settings.email.data.id}, {absolute: true});
                }

                if ((Settings.email.data.account ||
                    (Settings.email.data.contact && Settings.email.data.contact.accounts))) {
                    // Auto fill data if it's available.
                    if (Settings.email.data.contact && Settings.email.data.contact.id) {
                        if (Settings.email.data && Settings.email.data.account) {
                            const filterquery = 'accounts.id:' + Settings.email.data.account.id;

                            Contact.search({filterquery}).$promise.then(colleagues => {
                                for (let i = 0; i < colleagues.objects.length; i++) {
                                    if (colleagues.objects[i].id === Settings.email.data.contact.id) {
                                        vm.deal.contact = Settings.email.data.contact.id;
                                    }
                                }
                            });
                        } else {
                            vm.deal.contact = Settings.email.data.contact.id;
                        }
                    }

                    if (Settings.email.data && Settings.email.data.account) {
                        vm.deal.account = Settings.email.data.account.id;
                    }
                }
            }
        }

        if (vm.deal.next_step_date) {
            vm.deal.next_step_date = moment(vm.deal.next_step_date).toDate();
        }
    }

    $scope.$watchCollection('vm.deal.next_step', (newValue, oldValue) => {
        // Only change the next step date when the next step actually gets changed.
        // So don't change if we're just loading the deal (init when editing).
        if ((vm.deal && vm.deal.id && oldValue && newValue !== oldValue) || (!vm.deal.id && newValue !== oldValue)) {
            if (vm.deal.next_step.date_increment !== 0) {
                vm.deal.next_step_date = HLUtils.addBusinessDays(vm.deal.next_step.date_increment);
            } else if (angular.equals(vm.deal.next_step, vm.noneStep)) {
                // None step is selected, so clear the next step date.
                vm.deal.next_step_date = null;
            }
        }
    });

    $scope.$watch('vm.deal.status', () => {
        if (vm.deal && vm.lostStatus && vm.deal.id && vm.deal.status === vm.lostStatus.id) {
            if (vm.noneStep) {
                // If the status is 'Lost', set the next step to 'None'.
                vm.deal.next_step = vm.noneStep;
                vm.deal.next_step_date = null;
            }
        }
    });

    function assignToMe() {
        vm.deal.assigned_to = vm.currentUser;
    }

    function assignToMyTeams() {
        vm.deal.assigned_to_teams = vm.ownTeams;
    }

    function cancelDealCreation() {
        if ($scope.settings.email.sidebar.form === 'createDeal') {
            $scope.settings.email.sidebar.form = null;
            $scope.settings.email.sidebar.deal = false;
        } else {
            if (Settings.page.previousState && !Settings.page.previousState.state.abstract) {
                // Check if we're coming from another page.
                $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
            } else {
                $state.go('base.deals');
            }
        }
    }

    function saveDeal(form, archive) {
        // Check if a deal is being saved (and archived) via the + deal page
        // or via a supercard.
        if (Settings.email.sidebar.isVisible && archive) {
            ga('send', 'event', 'Deal', 'Save and archive', 'Email Sidebar');
        } else if (Settings.email.sidebar.isVisible && !archive) {
            ga('send', 'event', 'Deal', 'Save', 'Email Sidebar');
        } else if (!Settings.email.sidebar.isVisible && archive) {
            if ($stateParams.accountId) {
                ga('send', 'event', 'Deal', 'Save and archive', 'Account Widget');
            } else if ($stateParams.contactId) {
                ga('send', 'event', 'Deal', 'Save and archive', 'Contact Widget');
            } else {
                ga('send', 'event', 'Deal', 'Save and archive', 'Default');
            }
        } else {
            if ($stateParams.accountId) {
                ga('send', 'event', 'Deal', 'Save', 'Account Widget');
            } else if ($stateParams.contactId) {
                ga('send', 'event', 'Deal', 'Save', 'Contact Widget');
            } else {
                ga('send', 'event', 'Deal', 'Save', 'Default');
            }
        }

        if (!_dealFormIsValid()) {
            return;
        }

        HLForms.blockUI();
        HLForms.clearErrors(form);

        if (vm.deal.id) {
            if (!vm.deal.account) {
                vm.deal.account = null;
            }

            if (!vm.deal.contact) {
                vm.deal.contact = null;
            }

            if (!vm.deal.assigned_to) {
                vm.deal.assigned_to = null;
            }
        }

        if (archive) {
            vm.deal.is_archived = true;
        }

        // Clean modifies the object, so preserve the state by copying the object (in case of errors).
        const cleanedDeal = HLForms.clean(angular.copy(vm.deal));

        if (cleanedDeal.next_step_date) {
            cleanedDeal.next_step_date = moment(cleanedDeal.next_step_date).format('YYYY-MM-DD');
        }

        if (cleanedDeal.why_lost && cleanedDeal.status !== vm.lostStatus.id) {
            cleanedDeal.why_lost = null;
        }

        if (cleanedDeal.id) {
            // If there's an ID set it means we're dealing with an existing deal, so update it.
            cleanedDeal.$update(() => {
                toastr.success('I\'ve updated the deal for you!', 'Done');
                $state.go('base.deals.detail', {id: cleanedDeal.id}, {reload: true});
            }, response => {
                _handleBadResponse(response, form);
            });
        } else {
            cleanedDeal.$save(() => {
                new Intercom('trackEvent', 'deal-created');

                toastr.success('I\'ve saved the deal for you!', 'Yay');

                if (Settings.email.sidebar.form === 'deals') {
                    Settings.email.sidebar.form = null;

                    Metronic.unblockUI();
                } else {
                    $state.go('base.deals.detail', {id: cleanedDeal.id});
                }
            }, response => {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    $scope.$watch('vm.deal.account', (newValue, oldValue) => {
        // Get contacts who work for the selected account.
        refreshContacts('');

        // Only set business to 'existing' when adding a new deal or
        // changing to an account that has deals.
        if (vm.deal.account && ((vm.deal.id && oldValue && newValue !== oldValue) || (!vm.deal.id && newValue !== oldValue))) {
            // Mark as new business if the given account doesn't have any deals yet.
            const filterquery = `account.id:${vm.deal.account.id}`;
            Deal.search({filterquery}).$promise.then(response => {
                vm.deal.new_business = !response.objects.length;
            });
        }

        if (newValue !== oldValue) {
            _getOpenDeals();
        }
    });

    $scope.$watch('vm.deal.contact', (newValue, oldValue) => {
        if (vm.deal.contact && vm.deal.contact.accounts && vm.deal.contact.accounts.length) {
            // Get accounts that the select contact works for.
            vm.accounts = vm.deal.contact.accounts;
        } else {
            // Just get the accounts list.
            vm.accounts = null;
            refreshAccounts('');
        }

        if (newValue !== oldValue) {
            _getOpenDeals();
        }
    });

    function _getOpenDeals() {
        if (vm.deal.account || vm.deal.contact) {
            const filterQuery = 'NOT status.id:' + Deal.lostStatus.id + ' AND NOT status.id:' + Deal.wonStatus.id + ' AND is_archived: false';

            HLSearch.getOpenCasesDeals(filterQuery, vm.deal, 'Deal').then(response => {
                vm.openDeals = response.objects;
                vm.showSuggestions = true;
            });
        } else {
            vm.openDeals = [];
        }
    }

    $scope.$watch('vm.deal.assigned_to', (newValue, oldValue) => {
        let assignToTeams = [];

        if (vm.deal.assigned_to && oldValue && newValue !== oldValue) {
            for (let team of vm.teams) {
                if (vm.deal.assigned_to.teams && vm.deal.assigned_to.teams.indexOf(team.id) > -1) {
                    assignToTeams.push(team);
                }
            }

            vm.deal.assigned_to_teams = assignToTeams;
        }
    });

    function refreshAccounts(query) {
        // Don't load if we selected a contact.
        // Because we want to display all accounts the contact works for.
        if (!vm.deal.contact || query.length) {
            const accountsPromise = HLSearch.refreshList(query, 'Account');

            if (accountsPromise) {
                accountsPromise.$promise.then(data => {
                    vm.accounts = data.objects;
                });
            }
        }
    }

    function refreshContacts(query) {
        let accountQuery = '';

        if (vm.deal.account && vm.deal.account.id) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show active contacts of the selected account.
            accountQuery += 'active_at:' + vm.deal.account.id;
        }

        const contactsPromise = HLSearch.refreshList(query, 'Contact', accountQuery, '', 'full_name');

        if (contactsPromise) {
            contactsPromise.$promise.then(data => {
                vm.contacts = data.objects;
                if (vm.contacts.length === 1) {
                    vm.deal.contact = vm.contacts[0];
                }
            });
        }
    }

    function refreshUsers(query) {
        if (!vm.assigned_to || query.length) {
            const usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(data => {
                    vm.users = data.objects;
                });
            }
        }
    }

    function _dealFormIsValid() {
        if (!vm.deal.account && !vm.deal.contact) {
            swal({
                title: 'No account or contact',
                text: 'Please select an account or contact the deal belongs to',
                type: 'warning',
                confirmButtonText: 'Let me fix that for you',
            }).done();

            return false;
        }

        return true;
    }

    function _getTeams() {
        UserTeams.mine(response => {
            vm.ownTeams = response;
        });
    }

    $scope.$on('saveDeal', () => {
        saveDeal($scope.dealForm);
    });
}
