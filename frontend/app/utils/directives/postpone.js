angular.module('app.utils.directives').directive('postpone', postponeDirective);

function postponeDirective() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
            type: '=',
            dateField: '=',
            callback: '&',
            displayDate: '=',
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
        var modalInstance = $uibModal.open({
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
