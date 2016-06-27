/**
 * Router definition.
 */
angular.module('app.base').config(errorConfig);

errorConfig.$inject = ['$stateProvider'];
function errorConfig($stateProvider) {
    $stateProvider.state('base.500', {
        url: '/error',
        views: {
            '@': {
                templateUrl: 'base/errors/500.html',
                controller: ErrorController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Error',
        },
    });
}

angular.module('app.base').controller('ErrorController', ErrorController);

ErrorController.$inject = ['Settings'];
function ErrorController(Settings) {
    Settings.page.setAllTitles('custom', 'Error');
}
