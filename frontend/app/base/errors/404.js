/**
 * Router definition.
 */
angular.module('app.base').config(notFoundConfig);

notFoundConfig.$inject = ['$stateProvider'];
function notFoundConfig($stateProvider) {
    $stateProvider.state('base.404', {
        url: '/not-found',
        views: {
            '@': {
                templateUrl: 'base/errors/404.html',
                controller: NotFoundController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Not found',
        },
    });
}

angular.module('app.base').controller('NotFoundController', NotFoundController);

NotFoundController.$inject = ['Settings'];
function NotFoundController(Settings) {
    Settings.page.setAllTitles('custom', 'Not found');
}
