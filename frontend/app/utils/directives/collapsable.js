angular.module('app.utils.directives').directive('collapsable', CollapsableDirective);

CollapsableDirective.$inject = [];
function CollapsableDirective() {
    return {
        restrict: 'E',
        transclude: true,
        templateUrl: 'utils/directives/collapsable.html',
        controller: CollapsableController,
        controllerAs: 'cl',
        bindToController: true,
        scope: {
            name: '@',
        },
    };
}

CollapsableController.$inject = ['$scope', 'LocalStorage'];
function CollapsableController($scope, LocalStorage) {
    var vm = this;

    var storage = new LocalStorage('collapseDirective-' + vm.name);
    vm.folded = storage.get('folded', false);

    vm.toggleFolded = toggleFolded;

    function toggleFolded() {
        vm.folded = !vm.folded;
        storage.put('folded', vm.folded);
        $scope.$broadcast('foldedToggle', vm.folded);
    }
}
