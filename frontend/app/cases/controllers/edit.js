angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function (elem, attr) {
                    return '/cases/update/' + elem.id + '/';
                },
                controller: CaseEditController
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

angular.module('app.cases').controller('CaseEditController', CaseEditController);

CaseEditController.$inject = ['$scope', '$stateParams', 'Settings', 'CaseDetail'];
function CaseEditController ($scope, $stateParams, Settings, CaseDetail) {
    var id = $stateParams.id;
    var casePromise = CaseDetail.get({id: id}).$promise;

    casePromise.then(function(caseObject) {
        $scope.case = caseObject;
        Settings.page.setAllTitles('edit', $scope.case.subject);
        HLSelect2.init();
    });
}
