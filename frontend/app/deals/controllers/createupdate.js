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
        url: '/account/{id:[0-9]{1,}}',
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

DealCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Deal', 'HLForms', 'HLSearch', 'HLUtils', 'Settings', 'User'];
function DealCreateUpdateController($scope, $state, $stateParams, Account, Deal, HLForms, HLSearch, HLUtils, Settings, User) {
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
        _setAssignOptions();

        var choiceFields = ['found_through', 'contacted_by', 'currency', 'stage'];

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

        Deal.getFormOptions(function(data) {
            var choiceData = data.actions.POST;

            for (var i = 0; i < choiceFields.length; i++) {
                var splitName = choiceFields[i].split('_');
                var choiceVarName = splitName[0];

                // Convert to camelCase.
                if (splitName.length > 1) {
                    for (var j = 1; j < splitName.length; j++) {
                        choiceVarName += splitName[j].charAt(0).toUpperCase() + splitName[j].slice(1);
                    }
                }

                // Make the variable name a bit more logical (e.g. vm.stageChoices vs vm.stage).
                choiceVarName += 'Choices';

                vm[choiceVarName] = choiceData[choiceFields[i]].choices;
            }
        });

        _getDeal();
    }

    function _getDeal() {
        // Fetch the contact or create empty contact.
        if ($stateParams.id) {
            Deal.get({id: $stateParams.id}).$promise.then(function(deal) {
                vm.deal = deal;
                Settings.page.setAllTitles('edit', deal.name);

                if (deal.next_step_date) {
                    vm.originalNextStepDate = deal.next_step_date;
                }
            });
        } else {
            Settings.page.setAllTitles('create', 'deal');
            vm.deal = Deal.create();

            if ($scope.settings.email) {
                // Auto fill data if it's available.
                if ($scope.settings.email.accountId) {
                    vm.deal.account = $scope.settings.email.accountId;
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

    $scope.$watch('vm.deal.stage', function() {
        if (vm.deal.id && vm.deal.stage === 3) {
            if (vm.noneStep) {
                // If the stage is 'Lost', set the next step to 'None'.
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

    function assignToMe() {
        vm.deal.assigned_to = currentUser.id;
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

                if ($scope.settings.email.sidebar.form === 'createDeal') {
                    $scope.settings.email.sidebar.form = null;
                    $scope.settings.email.sidebar.deal = true;
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
        // Don't load if we selected a contact.
        // Because we want to display all accounts the contact works for.
        if (!vm.deal.contact && (!vm.accounts || query.length)) {
            vm.accounts = HLSearch.refreshList(query, 'Account');
        }
    }

    function refreshContacts(query) {
        var accountQuery = '';

        if (vm.deal.account) {
            if (query.length >= 2) {
                accountQuery += ' AND ';
            }

            // Only show contacts of the selected account.
            accountQuery += 'accounts.id:' + vm.deal.account.id;
        }

        vm.contacts = HLSearch.refreshList(query, 'Contact', null, accountQuery);
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
