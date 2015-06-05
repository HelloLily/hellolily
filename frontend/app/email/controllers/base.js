angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
function emailConfig($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/email', '/email/all/INBOX');
    $stateProvider.state('base.email', {
        url: '/email',
        views: {
            '@': {
                templateUrl: 'email/controllers/base.html',
                controller: EmailBaseController,
                controllerAs: 'vm'
            },
            'labelList@base.email': {
                templateUrl: 'email/controllers/label_list.html',
                controller: 'LabelListController',
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Email'
        },
        resolve: {
            primaryEmailAccountId: ['$q', 'User', function($q, User) {
                var deferred = $q.defer();
                User.me(null, function(data) {
                    deferred.resolve(data.primary_email_account);
                });
                return deferred.promise;
            }]
        }
    });
}

angular.module('app.email').controller('EmailBaseController', EmailBaseController);

EmailBaseController.$inject = ['$scope'];
function EmailBaseController ($scope) {
    $scope.conf.pageTitleBig = 'Email';
    $scope.conf.pageTitleSmall = 'sending love through the world!';
}
