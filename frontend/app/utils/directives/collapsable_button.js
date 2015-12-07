angular.module('app.utils.directives').directive('collapsableButton', CollapsableButtonDirective);

CollapsableButtonDirective.$inject = [];
function CollapsableButtonDirective() {
    return {
        restrict: 'E',
        require: '^collapsable',
        templateUrl: 'utils/directives/collapsable_button.html',
        link: function(scope, element, attrs, collapsableCtrl) {
            element.on('click', function() {
                collapsableCtrl.toggleFolded();
            });
        },
        controller: CollapsableButtonController,
        controllerAs: 'cl',
    };
}

CollapsableButtonController.$inject = ['$scope'];
function CollapsableButtonController($scope) {
    var vm = this;
    // Don't know why, but this controller is instantiated without the parent directive sometimes, somewhere...
    vm.folded = $scope.$parent.cl ? $scope.$parent.cl.folded : false;

    $scope.$on('foldedToggle', function(event, folded) {
        vm.folded = folded;
        $scope.$apply();
    });
}
