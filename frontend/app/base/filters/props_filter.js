angular.module('app.filters').filter('propsFilter', propsFilter);

function propsFilter() {
    return function(items, props) {
        var out = [];

        if (angular.isArray(items)) {
            items.forEach(function(item) {
                var i;
                var prop;
                var text;
                var itemMatches = false;
                var keys = Object.keys(props);

                for (i = 0; i < keys.length; i++) {
                    prop = keys[i];
                    text = props[prop].toLowerCase();

                    if (item[prop].toString().toLowerCase().indexOf(text) !== -1) {
                        itemMatches = true;
                        break;
                    }
                }

                if (itemMatches) {
                    out.push(item);
                }
            });
        } else {
            // Let the output be the input untouched.
            out = items;
        }

        return out;
    };
}
