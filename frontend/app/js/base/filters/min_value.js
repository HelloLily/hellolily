angular.module('app.filters').filter('minValue', minValue);
function minValue () {
    return function(values) {
        values.sort(function(a, b){return a-b});
        return values[0];
    }
}
