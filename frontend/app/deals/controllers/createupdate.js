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
    });
}

angular.module('app.deals').controller('DealCreateUpdateController', DealCreateUpdateController);

DealCreateUpdateController.$inject = ['$filter', '$scope', '$state', '$stateParams', 'Account', 'Contact', 'ContactDetail',
    'Deal', 'HLForms', 'HLSearch', 'HLUtils', 'Settings', 'User'];
function DealCreateUpdateController($filter, $scope, $state, $stateParams, Account, Contact, ContactDetail, Deal, HLForms,
                                    HLSearch, HLUtils, Settings, User) {
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

    activate();

    ////

    function activate() {
        var i;
        var j;
        var splitName = '';
        var choiceVarName = '';
        var choiceFields = ['currency'];

        _setAssignOptions();

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

        _getDeal();
    }

    function _getDeal() {
        var filterquery = '';

        // Fetch the contact or create empty contact.
        if ($stateParams.id) {
            Deal.get({id: $stateParams.id}).$promise.then(function(deal) {
                vm.deal = deal;

                vm.deal.amount_once = $filter('currency')(vm.deal.amount_once, '');
                vm.deal.amount_recurring = $filter('currency')(vm.deal.amount_recurring, '');

                Settings.page.setAllTitles('edit', deal.name);

                if (deal.next_step_date) {
                    vm.originalNextStepDate = deal.next_step_date;
                }
            });
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
                    // API returns 'full_name' but ES returns 'name'. So get the full name and set the name.
                    vm.deal.contact.name = contact.full_name;

                    if (vm.deal.contact.accounts && vm.deal.contact.accounts.length === 1) {
                        // Automatically fill in the account the contact works at.
                        vm.deal.account = vm.deal.contact.accounts[0];
                    }
                });
            }

            if (Settings.email.data && (Settings.email.data.account ||
                (Settings.email.data.contact && Settings.email.data.contact.accounts))) {
                // Auto fill data if it's available.
                if (Settings.email.data.contact.id) {
                    if (Settings.email.data && Settings.email.data.account) {
                        filterquery = 'accounts.id:' + Settings.email.data.account.id;

                        ContactDetail.query({filterquery: filterquery}).$promise.then(function(colleagues) {
                            var colleagueIds = [];
                            angular.forEach(colleagues, function(colleague) {
                                colleagueIds.push(colleague.id);
                            });

                            // Check if the contact actually works at the account.
                            if (colleagueIds.indexOf(Settings.email.data.contact.id) > -1) {
                                vm.deal.contact = Settings.email.data.contact.id;
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

    $scope.$watchCollection('vm.deal.next_step', function() {
        if (vm.deal.next_step) {
            if (vm.deal.next_step.date_increment !== 0) {
                vm.deal.next_step_date = HLUtils.addBusinessDays(vm.deal.next_step.date_increment, vm.originalNextStepDate);
            } else if (angular.equals(vm.deal.next_step, vm.noneStep)) {
                // None step is selected, so clear the next step date.
                vm.deal.next_step_date = null;
            }
        }
    });

    $scope.$watch('vm.deal.status', function() {
        if (vm.deal.id && vm.deal.status === vm.lostStatus.id) {
            if (vm.noneStep) {
                // If the status is 'Lost', set the next step to 'None'.
                vm.deal.next_step = vm.noneStep;
                vm.deal.next_step_date = null;
            }
        }
    });

    function _setAssignOptions() {
        var assignOptions = [];

        User.query().$promise.then(function(response) {
            angular.forEach(response.results, function(user) {
                if (user.first_name !== '') {
                    assignOptions.push(user);
                }
            });

            vm.assignOptions = assignOptions;
        });
    }

    function assignToMe() {
        // Bit of a hacky way to assign the current user, but we'll clean this up later.
        vm.deal.assigned_to = {id: currentUser.id, full_name: currentUser.fullName};
    }

    function cancelDealCreation() {
        if ($scope.settings.email.sidebar.form === 'createDeal') {
            $scope.settings.email.sidebar.form = null;
            $scope.settings.email.sidebar.deal = false;
        } else {
            $state.go('base.deals');
        }
    }

    function saveDeal(form, archive) {
        // Check if a deal is being saved (and archived) via the + deal page
        // or via a supercard.
        if (Settings.email.sidebar.isVisible && archive) {
            ga('send', 'event', 'Deal', 'Save and archive', 'Email SC');
        } else if (Settings.email.sidebar.isVisible && !archive) {
            ga('send', 'event', 'Deal', 'Save', 'Email SC');
        } else if (!Settings.email.sidebar.isVisible && archive) {
            ga('send', 'event', 'Deal', 'Save and archive', 'Deal');
        } else {
            ga('send', 'event', 'Deal', 'Save', 'Deal');
        }

        if (!_dealFormIsValid()) {
            return false;
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

        if (vm.deal.next_step_date) {
            vm.deal.next_step_date = moment(vm.deal.next_step_date).format('YYYY-MM-DD');
        }

        if (vm.deal.why_lost && vm.deal.status.id !== vm.lostStatus.id) {
            vm.deal.why_lost = null;
        }

        if (vm.deal.id) {
            // If there's an ID set it means we're dealing with an existing deal, so update it.
            vm.deal.$update(function() {
                toastr.success('I\'ve updated the deal for you!', 'Done');
                $state.go('base.deals.detail', {id: vm.deal.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            vm.deal.$save(function() {
                toastr.success('I\'ve saved the deal for you!', 'Yay');

                if (Settings.email.sidebar.form === 'deals') {
                    Settings.email.sidebar.form = null;

                    Metronic.unblockUI();
                } else {
                    $state.go('base.deals.detail', {id: vm.deal.id});
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
            Deal.query({filterquery: 'account:' + vm.deal.account.id}).$promise.then(function(response) {
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

        contactsPromise = HLSearch.refreshList(query, 'Contact', null, accountQuery);

        if (contactsPromise) {
            contactsPromise.$promise.then(function(data) {
                vm.contacts = data.objects;
                if (vm.contacts.length === 1) {
                    vm.deal.contact = vm.contacts[0];
                }
            });
        }
    }

    function _dealFormIsValid() {
        if (!vm.deal.account && !vm.deal.contact) {
            bootbox.dialog({
                message: 'Please select an account or contact the deal belongs to',
                title: 'No account or contact',
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
