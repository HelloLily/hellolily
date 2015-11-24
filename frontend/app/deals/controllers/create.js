angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig ($stateProvider) {
    $stateProvider.state('base.deals.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/deals/create',
                controller: DealCreateController
            }
        },
        ncyBreadcrumb: {
            label: 'New'
        }
    });
    $stateProvider.state('base.deals.create.fromAccount', {
        url: '/account/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: function(elem, attr) {
                    return '/deals/create/from_account/' + elem.id +'/';
                },
                controller: DealCreateController
            }
        },
        ncyBreadcrumb: {
            skip: true
        }
    });
}

angular.module('app.deals').controller('DealCreateController', DealCreateController);

DealCreateController.$inject = ['Settings'];
function DealCreateController (Settings) {
    Settings.page.setAllTitles('create', 'deal')
}
