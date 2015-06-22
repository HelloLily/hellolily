angular.module('app.directives').directive('countrySelector', countrySelector);

countrySelector.$inject = ['Country'];
function countrySelector(Country) {
    return {
        restrict: 'E',
        scope: {
            address: '='
        },
        templateUrl: 'forms/directives/country.html',
        link: function (scope) {
            scope.countries = [];
            Country.getList().then(function (countries) {
                scope.countries = countries;
            });
        }
    }
}
