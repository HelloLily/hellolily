/**
 * LilyServices is a container for all global lily related Angular services
 */
var lilyServices = angular.module('LilyServices', []);

/**
 * Cookie Service provides a simple interface to get and store cookie values
 *
 * Set `prefix` to give cookie keys a prefix
 */
lilyServices.factory('Cookie', ['$cookieStore', function ($cookieStore) {

    function CookieFactory (prefix) {
        return new Cookie(prefix);
    }

    function Cookie(prefix) {
        this.prefix = prefix;
    }

    /**
     * getCookieValue() tries to retrieve a value from the cookie, or returns default value
     *
     * @param field string: key to retrieve info from
     * @param defaultValue {*}: default value when nothing set on cache
     * @returns {*}: retrieved or default value
     */
    Cookie.prototype.get = function (field, defaultValue) {
        try {
            var value = $cookieStore.get(this.prefix + field);
            return (value !== undefined) ? value : defaultValue;
        } catch (error) {
            $cookieStore.remove(this.prefix + field);
            return defaultValue;
        }
    };

    /**
     * setCookieValue() sets value on the cookie
     *
     * It prefixes the field to make field unique for this controller
     *
     * @param field string: the key on which to store the value
     * @param value {*}: JSON serializable object to store
     */
    Cookie.prototype.put = function (field, value) {
        $cookieStore.put(this.prefix + field, value);
    };

    return CookieFactory;
}]);

lilyServices.service('HLDate', [function () {
    /**
     * getSubtractedDate() subtracts x amount of days from the current date
     *
     * @param days (int): amount of days to subtract from the current date
     *
     * @returns (string): returns the subtracted date in a yyyy-mm-dd format
     */
    this.getSubtractedDate = function (days) {
        var date = new Date();
        date.setDate(date.getDate() - days);

        return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
    };
}]);
lilyServices.service('HLText', [function () {
    /**
     * hlCapitalize() lowercases the whole string and makes the first character uppercase
     * This means 'STRING' becomes 'String'
     *
     * @returns (string): returns a string with only the first character uppercased
     */
    String.prototype.hlCapitalize = function () {
        var newString = this.toLowerCase();
        return newString.charAt(0).toUpperCase() + newString.substring(1);
    }
}]);
lilyServices.service('HLFilters', [function () {
    this.updateFilterQuery = function ($scope) {
        $scope.table.filterQuery = '';
        $scope.displayFilterClear = false;
        var filterStrings = [];

        for (var i = 0; i < $scope.filterList.length; i++) {
            var filter = $scope.filterList[i];
            if (filter.id && filter.id == 'archived') {
                if (!filter.selected) {
                    filterStrings.push('archived:false');
                }
                else {
                    $scope.displayFilterClear = true;
                }
            }
            else {
                if (filter.selected) {
                    filterStrings.push(filter.value);
                    $scope.displayFilterClear = true;
                }
            }
        }

        $scope.table.filterQuery = filterStrings.join(' AND ');
    };

    this.clearFilters = function ($scope) {
        for (var i = 0; i < $scope.filterList.length; i++) {
            $scope.filterList[i].selected = false;
        }

        $scope.updateFilterQuery();
    };
}]);

lilyServices.factory('Notifications', ['$resource', function($resource) {
    return $resource('/api/utils/notifications/');
}]);
