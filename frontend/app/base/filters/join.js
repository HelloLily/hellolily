/**
 * join takes the given array and joins the strings by the given delimiter (or comma if none is given).
 *
 * @param input {Array}: Array containing the strings (or objects).
 * @param field {string}: Field the string should be extracted from (if input contains objects).
 * @param delimited {string}: Character which seperates the strings.
 */
angular.module('app.filters').filter('join', join);

function join() {
    return function(input, field, delimiter) {
        var strings = [];
        var values = input;

        if (field) {
            // Array with object was given, so iterate over the objects and extract the field.
            angular.forEach(values, function(item) {
                strings.push(item[field]);
            });

            values = strings;
        }

        // Join the strings array.
        return (values || []).join(delimiter || ', ');
    };
}
