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
            var allCountries = [];
            scope.countries = [];

            Country.getList().then(function (countries) {
                allCountries = countries;
                scope.countries = allCountries.slice(0, 20);
            });
            scope.addMoreItems = function () {
                scope.countries = scope.countries.concat(allCountries.slice(scope.countries.length, scope.countries.length + 20));
            }
        }
    }
}
