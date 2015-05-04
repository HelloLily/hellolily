(function() {
    'use strict';

    /**
     * MyCases Widget
     */
    angular.module('app.dashboard.directives').directive('myCases', myCases);

    function myCases () {
        return {
            templateUrl: 'dashboard/mycases.html',
            controller: 'MyCases',
            controllerAs: 'mc'
        }
    }

    angular.module('app.dashboard.directives').controller('MyCases', MyCases);

    MyCases.$inject = ['$modal', 'Case'];
    function MyCases ($modal, Case) {
        var vm = this;
        vm.myCases = [];

        vm.openPostPoneWidget = openPostPoneWidget;

        activate();

        /////

        function activate() {
            _getMyCases();
        }

        function _getMyCases() {
            Case.getMyCasesWidget().then(function (data) {
                vm.myCases = data;
            });
        }

        function openPostPoneWidget(myCase) {
            var modalInstance = $modal.open({
                templateUrl: 'cases/casepostpone.modal.html',
                controller: 'CasePostponeModal',
                controllerAs: 'vm',
                size: 'sm',
                resolve: {
                    myCase: function() {
                        return myCase
                    }
                }
            });

            modalInstance.result.then(function() {
                _getMyCases();
            });
        }
    }
})();
