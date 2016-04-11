angular.module('app.utils.directives').directive('postpone', postponeDirective);

function postponeDirective() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
            type: '=',
            dateField: '=',
            callback: '&',
            ttPlacement: '@', // use tt instead of 'tooltip' for distinction.
        },
        templateUrl: 'utils/directives/postpone.html',
        controller: PostponeController,
        controllerAs: 'pp',  // naming it vm gives conflicts with the modal's scope
        bindToController: true,
    };
}

PostponeController.$inject = ['$state', '$uibModal'];
function PostponeController($state, $uibModal) {
    var pp = this;

    pp.openPostponeModal = openPostponeModal;

    function openPostponeModal() {
        var modalInstance;

        // Google Analytics events per page to track where users use the
        // postpone functionality.
        if ($state.current.name === 'base.dashboard') {
            ga('send', 'event', pp.type, 'Open postpone modal', 'Dashboard');
        }

        if ($state.current.name === 'base.cases.detail') {
            ga('send', 'event', 'Case', 'Open postpone modal', 'Case detail');
        }

        if ($state.current.name === 'base.cases') {
            ga('send', 'event', 'Case', 'Open postpone modal', 'Cases list view');
        }

        if ($state.current.name === 'base.deals.detail') {
            ga('send', 'event', 'Deal', 'Open postpone modal', 'Deal detail');
        }

        if ($state.current.name === 'base.deals') {
            ga('send', 'event', 'Deal', 'Open postpone modal', 'Deal list view');
        }

        if ($state.current.name === 'base.accounts.detail') {
            ga('send', 'event', pp.type, 'Open postpone modal', 'Account detail');
        }

        if ($state.current.name === 'base.contacts.detail') {
            ga('send', 'event', pp.type, 'Open postpone modal', 'Deal detail');
        }

        modalInstance = $uibModal.open({
            templateUrl: 'utils/controllers/postpone.html',
            controller: 'PostponeModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                data: function() {
                    return {
                        object: pp.object,
                        dateField: pp.dateField,
                        type: pp.type,
                    };
                },
            },
        });

        modalInstance.result.then(function() {
            if (pp.callback) {
                pp.callback();
            } else {
                $state.go($state.current, {}, {reload: true});
            }
        });
    }
}
