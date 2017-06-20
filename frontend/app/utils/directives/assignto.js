angular.module('app.utils.directives').directive('assignTo', assignToDirective);

function assignToDirective() {
    return {
        restrict: 'E',
        scope: {
            object: '<',
            type: '@',
        },
        templateUrl: 'utils/directives/assignto.html',
        controller: AssignToController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

AssignToController.$inject = ['$compile', '$injector', '$scope', '$state', '$templateCache', '$timeout',
    'HLResource', 'HLSearch', 'HLUtils'];
function AssignToController($compile, $injector, $scope, $state, $templateCache, $timeout,
    HLResource, HLSearch, HLUtils) {
    var vm = this;

    vm.assignTo = assignTo;
    vm.assignToMe = assignToMe;
    vm.refreshUsers = refreshUsers;

    function assignTo(myCase) {
        swal({
            title: sprintf(messages.alerts.assignTo.title, {type: vm.type.toLowerCase()}),
            html: $compile($templateCache.get('utils/directives/assignto_modal.html'))($scope),
            showCancelButton: true,
            showCloseButton: true,
        }).then(function(isConfirm) {
            if (isConfirm) {
                $injector.get(vm.type).patch({id: vm.object.id, assigned_to: vm.assigned_to.id}).$promise.then(function() {
                    $state.go($state.current, {}, {reload: true});
                });
            }
        }).done();
    }

    function assignToMe() {
        vm.assigned_to = {
            id: currentUser.id,
            full_name: currentUser.fullName,
        };
    }

    function refreshUsers(query) {
        var usersPromise;

        if (!vm.assigned_to || query.length) {
            usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(function(data) {
                    vm.users = data.objects;
                });
            }
        }
    }
}
