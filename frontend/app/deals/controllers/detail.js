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
            currentDeal: ['Deal', '$stateParams', (Deal, $stateParams) => Deal.get({id: $stateParams.id}).$promise],
            dealAccount: ['Account', 'currentDeal', (Account, currentDeal) => {
                let account;

                if (currentDeal.account) {
                    account = Account.get({id: currentDeal.account.id, filter_deleted: 'False'}).$promise;
                }

                return account;
            }],
            dealContact: ['Contact', 'currentDeal', (Contact, currentDeal) => {
                let contact;

                if (currentDeal.contact) {
                    contact = Contact.get({id: currentDeal.contact.id, filter_deleted: 'False'}).$promise;
                }

                return contact;
            }],
            user: ['User', User => User.me().$promise],
            tenant: ['Tenant', Tenant => Tenant.query({})],
            timeLogs: ['TimeLog', 'currentDeal', (TimeLog, currentDeal) => {
                return TimeLog.getForObject({id: currentDeal.id, model: 'deals'}).$promise;
            }],
        },
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'Account', 'Contact', 'Deal',
    'HLResource', 'HLUtils', 'LocalStorage', 'Settings', 'Tenant', 'currentDeal', 'dealAccount', 'dealContact',
    'user', 'tenant', 'timeLogs'];
function DealDetailController($compile, $scope, $state, $templateCache, Account, Contact, Deal,
    HLResource, HLUtils, LocalStorage, Settings, Tenant, currentDeal, dealAccount, dealContact,
    user, tenant, timeLogs) {
    const vm = this;
    const storage = new LocalStorage('dealDetail');

    let activeAt = true;

    if (dealContact) {
        activeAt = dealContact.active_at_account[currentDeal.account.id];
    }

    Settings.page.setAllTitles('detail', currentDeal.name, currentDeal.contact, currentDeal.account, null, activeAt);
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
    vm.deal.timeLogs = timeLogs.objects;
    vm.currentUser = user;
    vm.tenant = tenant;
    vm.mergeStreams = storage.get('mergeStreams', false);

    vm.changeState = changeState;
    vm.updateModel = updateModel;
    vm.assignDeal = assignDeal;

    activate();

    //////

    function activate() {
        Deal.getNextSteps(response => {
            response.results.forEach(nextStep => {
                if (nextStep.name === 'None') {
                    vm.noneStep = nextStep;
                }
            });
        });

        Deal.getWhyLost(response => {
            vm.whyLostChoices = response.results;
        });

        Deal.getStatuses(response => {
            vm.statusChoices = response.results;

            vm.lostStatus = Deal.lostStatus;
            vm.wonStatus = Deal.wonStatus;
        });

        if (vm.tenant.hasPandaDoc && vm.deal.contact) {
            Deal.getDocuments({contact: vm.deal.contact.id}, response => {
                const documents = response.documents;

                documents.forEach(document => {
                    document.status = document.status.replace('document.', '');
                });

                vm.documents = documents;
            });
        }

        vm.dealStart = moment(vm.deal.created).subtract(2, 'days').format('YYYY-MM-DD');

        let dealEnd;

        if (vm.deal.status.id === vm.lostStatus || vm.deal.status.id === vm.wonStatus) {
            dealEnd = moment(vm.deal.modified);
        } else {
            dealEnd = moment();
        }

        vm.dealEnd = dealEnd.add(2, 'days').format('YYYY-MM-DD');
    }

    function updateModel(data, field) {
        const args = HLResource.createArgs(data, field, vm.deal);

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
            return Account.patch(args, () => {
                toastr.success('I\'ve updated the customer ID for you!', 'Done');
            });
        }

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data, vm.deal.contact, vm.deal.account);
        }

        const patchPromise = HLResource.patch('Deal', args).$promise;

        patchPromise.then(response => {
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
        // For now we'll use a separate function to update the status,
        // since the buttons and the value in the list need to be equal.
        vm.deal.status = status;

        // TODO: Should this be done in the API?
        if (['Won', 'Lost'].indexOf(status[1]) > -1) {
            vm.deal.closed_date = moment().format();
        } else {
            vm.deal.closed_date = null;
        }

        const args = {
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

    $scope.$watch('vm.deal.is_archived', (newValue, oldValue) => {
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
        }).then(isConfirm => {
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

    $scope.$watch('vm.mergeStreams', () => {
        storage.put('mergeStreams', vm.mergeStreams);
    });
}
