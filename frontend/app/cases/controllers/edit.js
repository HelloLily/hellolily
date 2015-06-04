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

CaseEditController.$inject = ['$scope', '$stateParams', 'CaseDetail'];
function CaseEditController ($scope, $stateParams, CaseDetail) {
    var id = $stateParams.id;
    var casePromise = CaseDetail.get({id: id}).$promise;

    casePromise.then(function(caseObject) {
        $scope.case = caseObject;
        $scope.conf.pageTitleBig = caseObject.subject;
        $scope.conf.pageTitleSmall = 'change is natural';
        HLSelect2.init();
    });
}
