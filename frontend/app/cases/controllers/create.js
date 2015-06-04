angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig ($stateProvider) {
    $stateProvider.state('base.cases.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/cases/create',
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });
    $stateProvider.state('base.cases.create.fromContact', {
        url: '/contact/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_contact/' + elem.id +'/';
                },
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
    $stateProvider.state('base.cases.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/cases/create/from_account/' + elem.id +'/';
                },
                controller: CaseCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}

angular.module('app.cases').controller('CaseCreateController', CaseCreateController);

CaseCreateController.$inject = ['$scope'];
function CaseCreateController ($scope) {
    $scope.conf.pageTitleBig = 'New case';
    $scope.conf.pageTitleSmall = 'making cases';
    HLCases.addAssignToMeButton();
    HLSelect2.init();
}
