 angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals.detail', {
        url: '/{id:[0-9]{1,}}',
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
        },
    });
}

angular.module('app.deals').controller('DealDetailController', DealDetailController);

DealDetailController.$inject = ['$scope', 'Deal', 'DealStages', 'HLResource', 'HLUtils', 'Settings', 'currentDeal'];
function DealDetailController($scope, Deal, DealStages, HLResource, HLUtils, Settings, currentDeal) {
    var vm = this;

    Settings.page.setAllTitles('detail', currentDeal.name);

    vm.deal = currentDeal;
    vm.dealStages = DealStages.query();

    vm.changeState = changeState;
    vm.updateModel = updateModel;

    activate();

    //////

    function activate() {
        Deal.getNextSteps(function(response) {
            angular.forEach(response.results, function(nextStep) {
                if (nextStep.name === 'None') {
                    vm.noneStep = nextStep;
                }
            });
        });

        if (vm.deal.next_step_date) {
            vm.originalNextStepDate = vm.deal.next_step_date;
        }
    }

    function updateModel(data, field) {
        var args;

        if (typeof data === 'object') {
            args = data;
        } else {
            args = {
                id: vm.deal.id,
            };

            args[field] = data;

            if (field === 'name') {
                Settings.page.setAllTitles('detail', data);
            }
        }

        if (args.hasOwnProperty('next_step')) {
            if (vm.deal.next_step.date_increment !== 0) {
                // Update next step date based on next step.
                var nextStepDate = HLUtils.addBusinessDays(vm.deal.next_step.date_increment, vm.originalNextStepDate);
                nextStepDate = moment(nextStepDate).format('YYYY-MM-DD');
                vm.deal.next_step_date = nextStepDate;
            } else if (angular.equals(vm.deal.next_step, vm.noneStep)) {
                // None step is selected, so clear the next step date.
                vm.deal.next_step_date = null;
            }
        }

        if (args.hasOwnProperty('stage')) {
            if (vm.deal.stage === 3) {
                // If the stage is 'Lost', set the next step to 'None'.
                vm.deal.next_step = vm.noneStep;
                vm.deal.next_step_date = null;
            }
        }

        return HLResource.patch('Deal', args).$promise;
    }

    /**
     * Change the state of a deal.
     */
    function changeState(stage) {
        // For now we'll use a separate function to update the stage,
        // since the buttons and the value in the list need to be equal.
        vm.deal.stage = stage[0]; // ID of the stage
        vm.deal.stage_display = stage[1]; // Name of the stage

        // TODO: Should this be done in the API?
        if (['Won', 'Lost'].indexOf(stage[1]) > -1) {
            vm.deal.closed_date = moment().format();
        } else {
            vm.deal.closed_date = null;
        }

        var args = {
            id: vm.deal.id,
            stage: vm.deal.stage,
            closed_date: vm.deal.closed_date,
        };

        return HLResource.patch('Deal', args).$promise;
    }

    $scope.$watch('vm.deal.is_archived', function(newValue, oldValue) {
        if (newValue !== oldValue) {
            updateModel(vm.deal.is_archived, 'is_archived');
        }
    });
}
