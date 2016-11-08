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
            currentDeal: function() {
                return null;
            },
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
            currentDeal: function() {
                return null;
            },
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
            currentDeal: function() {
                return null;
            },
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
            currentDeal: ['Deal', '$stateParams', function(Deal, $stateParams) {
                var id = $stateParams.id;
                return Deal.get({id: id}).$promise;
            }],
        },
    });
}

angular.module('app.deals').controller('DealCreateUpdateController', DealCreateUpdateController);

DealCreateUpdateController.$inject = ['$filter', '$scope', '$state', '$stateParams', 'Account', 'Contact', 'Deal',
    'HLForms', 'HLSearch', 'HLUtils', 'Settings', 'Tenant', 'User', 'currentDeal'];
function DealCreateUpdateController($filter, $scope, $state, $stateParams, Account, Contact, Deal, HLForms,
                                    HLSearch, HLUtils, Settings, Tenant, User, currentDeal) {
    var vm = this;

    vm.deal = {};
    vm.datepickerOptions = {
        startingDay: 1,
    };
    vm.configDealType = 0;

    vm.assignToMe = assignToMe;
    vm.cancelDealCreation = cancelDealCreation;
    vm.saveDeal = saveDeal;
    vm.refreshAccounts = refreshAccounts;
    vm.refreshContacts = refreshContacts;
    vm.refreshUsers = refreshUsers;

    activate();

    ////

    function activate() {
        var i;
        var j;
        var splitName = '';
        var choiceVarName = '';
        var choiceFields = ['currency'];

        Deal.getNextSteps(function(response) {
            vm.nextSteps = response.results;

            angular.forEach(response.results, function(nextStep) {
                if (nextStep.name === 'None') {
                    vm.noneStep = nextStep;
                }
            });
        });

        Deal.getWhyCustomer(function(response) {
            vm.whyCustomer = response.results;
        });

        Deal.getWhyLost(function(response) {
            vm.whyLost = response.results;
        });

        Deal.getFoundThrough(function(response) {
            vm.foundThroughChoices = response.results;
        });

        Deal.getContactedBy(function(response) {
            vm.contactedByChoices = response.results;
        });

        Deal.getStatuses(function(response) {
            vm.statusChoices = response.results;

            vm.lostStatus = Deal.lostStatus;
            vm.wonStatus = Deal.wonStatus;
        });

        Deal.getFormOptions(function(data) {
            var choiceData = data.actions.POST;

            for (i = 0; i < choiceFields.length; i++) {
                splitName = choiceFields[i].split('_');
                choiceVarName = splitName[0];

                // Convert to camelCase.
                if (splitName.length > 1) {
                    for (j = 1; j < splitName.length; j++) {
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

        Tenant.query({}, function(tenant) {
            vm.tenant = tenant;
        });

        _getDeal();
    }

    function _getDeal() {
        var filterquery = '';
        var i;

        // Fetch the contact or create empty contact.
        if (currentDeal) {
            vm.deal = currentDeal;

            vm.deal.amount_once = $filter('currency')(vm.deal.amount_once, '');
            vm.deal.amount_recurring = $filter('currency')(vm.deal.amount_recurring, '');

            Settings.page.setAllTitles('edit', currentDeal.name);
        } else {
            Settings.page.setAllTitles('create', 'deal');
            vm.deal = Deal.create();

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}).$promise.then(function(account) {
                    vm.deal.account = account;
                });
            }

            if ($stateParams.contactId) {
                Contact.get({id: $stateParams.contactId}).$promise.then(function(contact) {
                    vm.deal.contact = contact;

                    if (vm.deal.contact.accounts && vm.deal.contact.accounts.length === 1) {
                        // Automatically fill in the account the contact works at.
                        vm.deal.account = vm.deal.contact.accounts[0];
                    }
                });
            }

            if (Settings.email.data && (Settings.email.data.account ||
                (Settings.email.data.contact && Settings.email.data.contact.accounts))) {
                // Auto fill data if it's available.
                if (Settings.email.data.contact && Settings.email.data.contact.id) {
                    if (Settings.email.data && Settings.email.data.account) {
                        filterquery = 'accounts.id:' + Settings.email.data.account.id;

                        Contact.search({filterquery: filterquery}).$promise.then(function(colleagues) {
                            for (i = 0; i < colleagues.objects.length; i++) {
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

        vm.deal.next_step_date = moment(vm.deal.next_step_date).toDate();
    }

    $scope.$watchCollection('vm.deal.next_step', function(newValue, oldValue) {
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

    $scope.$watch('vm.deal.status', function() {
        if (vm.deal && vm.lostStatus && vm.deal.id && vm.deal.status === vm.lostStatus.id) {
            if (vm.noneStep) {
                // If the status is 'Lost', set the next step to 'None'.
                vm.deal.next_step = vm.noneStep;
                vm.deal.next_step_date = null;
            }
        }
    });

    function assignToMe() {
        // Bit of a hacky way to assign the current user, but we'll clean this up later.
        vm.deal.assigned_to = {id: currentUser.id, full_name: currentUser.fullName};
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
        var copiedDeal;

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
        }

        if (archive) {
            vm.deal.is_archived = true;
        }

        copiedDeal = angular.copy(vm.deal);

        if (copiedDeal.next_step_date) {
            copiedDeal.next_step_date = moment(copiedDeal.next_step_date).format('YYYY-MM-DD');
        }

        if (copiedDeal.why_lost && copiedDeal.status.id !== vm.lostStatus.id) {
            copiedDeal.why_lost = null;
        }

        if (copiedDeal.id) {
            // If there's an ID set it means we're dealing with an existing deal, so update it.
            copiedDeal.$update(function() {
                toastr.success('I\'ve updated the deal for you!', 'Done');
                $state.go('base.deals.detail', {id: copiedDeal.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            copiedDeal.$save(function() {
                new Intercom('trackEvent', 'deal-created');

                toastr.success('I\'ve saved the deal for you!', 'Yay');

                if (Settings.email.sidebar.form === 'deals') {
                    Settings.email.sidebar.form = null;

                    Metronic.unblockUI();
                } else {
                    $state.go('base.deals.detail', {id: copiedDeal.id});
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

    $scope.$watch('vm.deal.account', function() {
        // Get contacts that work for the selected account.
        refreshContacts('');

        if (vm.deal.account) {
            // Mark as new business if the given account doesn't have any deals yet.
            Deal.query({filterquery: 'account.id:' + vm.deal.account.id}).$promise.then(function(response) {
                vm.deal.new_business = !response.objects.length;
            });
        }
    });

    $scope.$watch('vm.deal.contact', function() {
        if (vm.deal.contact && vm.deal.contact.accounts && vm.deal.contact.accounts.length) {
            // Get accounts that the select contact works for.
            vm.accounts = vm.deal.contact.accounts;
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
        if (!vm.deal.contact && (!vm.accounts || query.length)) {
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

        if (vm.deal.account) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show contacts of the selected account.
            accountQuery += 'accounts.id:' + vm.deal.account.id;
        }

        contactsPromise = HLSearch.refreshList(query, 'Contact', accountQuery, '', 'full_name');

        if (contactsPromise) {
            contactsPromise.$promise.then(function(data) {
                vm.contacts = data.objects;
                if (vm.contacts.length === 1) {
                    vm.deal.contact = vm.contacts[0];
                }
            });
        }
    }

    function refreshUsers(query) {
        var usersPromise;

        if (!vm.assigned_to && (!vm.users || query.length)) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(function(data) {
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
                confirmButtonClass: 'btn btn-success',
            }).done();

            return false;
        }

        return true;
    }

    $scope.$on('saveDeal', function() {
        saveDeal($scope.dealForm);
    });
}
