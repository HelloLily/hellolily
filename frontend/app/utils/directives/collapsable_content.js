angular.module('app.utils.directives').directive('collapsableContent', CollapsableContentDirective);

CollapsableContentDirective.$inject = [];
function CollapsableContentDirective () {
    return {
        restrict: 'E',
        templateUrl: 'utils/directives/collapsable_content.html',
        transclude: true,
        require: '^collapsable',
        controller: CollapsableContentController,
        controllerAs: 'cl'
    }
}

CollapsableContentController.$inject = ['$scope'];
function CollapsableContentController ($scope) {
    var vm = this;
    // Don't know why, but this controller is instantiated without the parent directive sometimes, somewhere...
    vm.folded = $scope.$parent.cl ? $scope.$parent.cl.folded : false;

    $scope.$on('foldedToggle', function (event, folded) {
        vm.folded = folded;
        $scope.$apply();
    });
}
