(function() {
    'use strict';

    angular.module('app.cases.directives', []);

    angular.module('app.cases.directives').directive('updateCaseExpireDate', updateCaseExpireDate);

    updateCaseExpireDate.$inject = ['$rootScope'];
    function updateCaseExpireDate ($rootScope) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {

                var select = $('#id_priority');
                var daysToAdd = [5, 3, 1, 0];

                select.on('change', function(event) {
                    var priority = parseInt(select.val());
                    if(isNaN(select.val())){
                        priority = 3;
                    }
                    var due = addBusinessDays(new Date(), daysToAdd[priority]);
                    var month = due.getMonth() + 1;
                    if(month < 10){
                        month = '0' + month;
                    }
                    var expires = due.getDate() + '/' + month + '/' + due.getFullYear();
                    $('#id_expires').val(expires);
                    $('#id_expires_picker').datepicker('update', expires);
                });
            }
        }
    }

    angular.module('app.cases.directives').directive('caseListWidget', CaseListWidget);
    function CaseListWidget(){
        return {
            restrict: 'E',
            replace: true,
            scope: {
                title: '@',
                list: '=',
                height: '=',
                addLink: '@'
            },
            templateUrl: 'cases/directives/list-widget.html'
        }
    }
})();
