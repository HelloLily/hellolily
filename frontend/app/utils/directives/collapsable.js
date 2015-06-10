angular.module('app.utils.directives').directive('collapsable', CollapsableDirective);

CollapsableDirective.$inject = [];
function CollapsableDirective () {
    return {
        restrict: 'E',
        transclude: true,
        templateUrl: 'utils/directives/collapsable.html',
        controller: CollapsableController,
        controllerAs: 'cl',
        bindToController: true,
        scope: {
            name: '@'
        }
    }
}

CollapsableController.$inject = ['$scope', 'Cookie'];
function CollapsableController ($scope, Cookie) {
    var vm = this;

    var cookie = Cookie('collapseDirective-' + vm.name);
    vm.folded = cookie.get('folded', false);

    vm.toggleFolded = toggleFolded;

    function toggleFolded () {
        vm.folded = !vm.folded;
        cookie.put('folded', vm.folded);
        $scope.$broadcast('foldedToggle', vm.folded);
    }
}
