angular.module('app.filters').filter('currencySymbol', currencySymbol);

currencySymbol.$inject = ['$filter'];
function currencySymbol($filter) {
    var currencySymbols = {
        'EUR': '&#8364; ',
        'GBP': '&#163; ',
        'USD': '&#36; ',
        'ZAR': '&#82; ',
        'NOR': '&#107;&#114; ',
        'DKK': '&#107;&#114; ',
        'SEK': '&#107;&#114; ',
        'CHF': '&#67;&#72;&#70; ',
    };

    return function(amount, currency) {
        return $filter('currency')(amount, currencySymbols[currency]);
    };
}
