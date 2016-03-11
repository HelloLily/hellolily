angular.module('app.filters').filter('inArray', inArray);

function inArray() {
    return function(array, value) {
        return array.indexOf(value) !== -1;
    };
}
