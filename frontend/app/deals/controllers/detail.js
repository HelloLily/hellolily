angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals.detail', {
        parent: 'base.deals',
        url: '/{id:int}',
        views: {
            '@': {
                templateUrl: 'deals/controllers/detail.html',
                controller: DealDetailController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: '{{ deal.name }}',
        },
        resolve: {
            currentDeal: ['Deal', '$stateParams', function(Deal, $stateParams) {
                var id = $stateParams.id;
                return Deal.get({id: id}).$promise;
            }],
            dealAccount: ['Account', 'currentDeal', function(Account, currentDeal) {
                var account;

                if (currentDeal.account) {
                    account = Account.get({id: currentDeal.account.id, filter_deleted: 'False'}).$promise;
                }

                return account;
            }],
            dealContact: ['Contact', 'currentDeal', function(Contact, currentDeal) {
                var contact;

                if (currentDeal.contact) {
                    contact = Contact.get({id: currentDeal.contact.id, filter_deleted: 'False'}).$promise;
                }

                return contact;
            }],
            user: ['User', function(User) {
                return User.me().$promise;
            }],
            tenant: ['Tenant', function(Tenant) {
                return Tenant.query({});
            }],
        },
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'Account', 'Contact', 'Deal',
    'HLResource', 'HLUtils', 'LocalStorage', 'Settings', 'Tenant', 'currentDeal', 'dealAccount', 'dealContact',
    'user', 'tenant'];
function DealDetailController($compile, $scope, $state, $templateCache, Account, Contact, Deal,
                              HLResource, HLUtils, LocalStorage, Settings, Tenant, currentDeal, dealAccount, dealContact,
                              user, tenant) {
    var vm = this;
    var storage = new LocalStorage('dealDetail');

    Settings.page.setAllTitles('detail', currentDeal.name, currentDeal.contact, currentDeal.account);
    Settings.page.toolbar.data = {
        model: 'Deal',
        object: currentDeal,
        field: 'name',
        updateCallback: updateModel,
        formName: 'dealHeaderForm',
    };

    vm.deal = currentDeal;
    vm.deal.account = dealAccount;
    vm.deal.contact = dealContact;
    vm.currentUser = user;
    vm.tenant = tenant;
    vm.mergeHistory = storage.get('mergeHistory', false);

    vm.changeState = changeState;
    vm.updateModel = updateModel;
    vm.assignDeal = assignDeal;

    activate();

    //////

    function activate() {
        var dealEnd;

        Deal.getNextSteps(function(response) {
            angular.forEach(response.results, function(nextStep) {
                if (nextStep.name === 'None') {
                    vm.noneStep = nextStep;
                }
            });
        });

        Deal.getWhyLost(function(response) {
            vm.whyLostChoices = response.results;
        });

        Deal.getStatuses(function(response) {
            vm.statusChoices = response.results;

            vm.lostStatus = Deal.lostStatus;
            vm.wonStatus = Deal.wonStatus;
        });

        if (vm.tenant.hasPandaDoc && vm.deal.contact) {
            Deal.getDocuments({contact: vm.deal.contact.id}, function(response) {
                var documents = response.documents;

                documents.forEach(function(document) {
                    document.status = document.status.replace('document.', '');
                });

                vm.documents = documents;
            });
        }

        vm.dealStart = moment(vm.deal.created).subtract(2, 'days').format('YYYY-MM-DD');

        if (vm.deal.status.id === vm.lostStatus || vm.deal.status.id === vm.wonStatus) {
            dealEnd = moment(vm.deal.modified);
        } else {
            dealEnd = moment();
        }

        vm.dealEnd = dealEnd.add(2, 'days').format('YYYY-MM-DD');
    }

    function updateModel(data, field) {
        var args = HLResource.createArgs(data, field, vm.deal);
        var patchPromise;

        if (args.hasOwnProperty('status')) {
            args.status = args.status.id;

            if (vm.deal.status.id === vm.lostStatus.id) {
                // If the status is 'Lost', set the next step to 'None'.
                vm.deal.next_step = vm.noneStep;
                vm.deal.next_step_date = null;

                args.next_step = vm.noneStep.id;
                args.next_step_date = null;
            } else {
                vm.deal.why_lost = null;

                args.why_lost = null;
            }
        }

        if (args.hasOwnProperty('assigned_to_teams')) {
            const oldTeams = vm.deal.assigned_to_teams.map(team => ({'id': team.id}));
            const teamIds = args.assigned_to_teams.map(team => team.id);
            let removedTeams = oldTeams.filter(team => teamIds.indexOf(team.id) === -1);
            for (let team of removedTeams) team.is_deleted = true;
            args.assigned_to_teams = args.assigned_to_teams.map(team => ({'id': team.id})).concat(removedTeams);
        }

        if (args.hasOwnProperty('customer_id')) {
            vm.deal.account.customer_id = args.customer_id;

            // Updating an object through another object (e.g. account through deal) is ugly.
            // So just do a separate Account.patch. Not using the HLResource.patch because we want to display
            // a custom message.
            return Account.patch(args, function() {
                toastr.success('I\'ve updated the customer ID for you!', 'Done');
            });
        }

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data, vm.deal.contact, vm.deal.account);
        }

        patchPromise = HLResource.patch('Deal', args).$promise;

        patchPromise.then(function(response) {
            if (response.hasOwnProperty('next_step')) {
                vm.deal.next_step_date = response.next_step_date;
            }

            if (args.hasOwnProperty('amount_once') || args.hasOwnProperty('amount_recurring')) {
                $state.go($state.current, {}, {reload: true});
            }
        });

        return patchPromise;
    }

    /**
     * Change the state of a deal.
     */
    function changeState(status) {
        var args;

        // For now we'll use a separate function to update the status,
        // since the buttons and the value in the list need to be equal.
        vm.deal.status = status;

        // TODO: Should this be done in the API?
        if (['Won', 'Lost'].indexOf(status[1]) > -1) {
            vm.deal.closed_date = moment().format();
        } else {
            vm.deal.closed_date = null;
        }

        args = {
            id: vm.deal.id,
            status: vm.deal.status,
            closed_date: vm.deal.closed_date,
        };

        if (vm.deal.status.id === vm.lostStatus.id && vm.whyLostChoices.length > 0) {
            // If the status is 'Lost' we want to provide a reason why the deal was lost.
            whyLost(args);
        } else {
            updateModel(args);
        }
    }

    $scope.$watch('vm.deal.is_archived', function(newValue, oldValue) {
        if (newValue !== oldValue) {
            updateModel(vm.deal.is_archived, 'is_archived');
        }
    });

    function whyLost(args) {
        swal({
            title: messages.alerts.deals.title,
            html: $compile($templateCache.get('deals/controllers/whylost.html'))($scope),
            showCancelButton: true,
            showCloseButton: true,
        }).then(function(isConfirm) {
            if (isConfirm) {
                vm.deal.why_lost = vm.whyLost;
                args.why_lost = vm.whyLost.id;

                updateModel(args);
            }
        }).done();
    }

    function assignDeal() {
        vm.deal.assigned_to = currentUser;
        vm.deal.assigned_to.full_name = currentUser.fullName;

        // Broadcast function to update model correctly after dynamically
        // changing the assignee by using the 'assign to me' link.
        $scope.$broadcast('activateEditableSelect', currentUser.id);

        return updateModel(currentUser.id, 'assigned_to');
    }

    $scope.$watch('vm.mergeHistory', function() {
        storage.put('mergeHistory', vm.mergeHistory);
    });
}
