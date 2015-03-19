/**
 * lilyServices is a container for all global lily related Angular services
 */
angular.module('lilyServices', [])

    /**
     * Cookie Service provides a simple interface to get and store cookie values
     *
     * Set `prefix` to give cookie keys a prefix
     */
    .service('Cookie', ['$cookieStore', function($cookieStore) {

        /**
         * prefix is used to add as a prefix to the field name.
         *
         * @type {string}
         */
        this.prefix = '';

        /**
         * getCookieValue() tries to retrieve a value from the cookie, or returns default value
         *
         * @param field string: key to retrieve info from
         * @param defaultValue {*}: default value when nothing set on cache
         * @returns {*}: retrieved or default value
         */
        this.getCookieValue = function(field, defaultValue) {
            var value = $cookieStore.get(this.prefix + field);
            if (value !== undefined) {
                return value;
            } else {
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
        this.setCookieValue = function(field, value) {
            $cookieStore.put(this.prefix + field, value);
        };

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        this.getCsrftoken = function() {
            if (!this._csrftoken) {
                this._csrftoken = getCookie('csrftoken');
                $cookieStore.put('x-csrftoken', this._csrftoken);
            }
            return this._csrftoken;
        };
    }])
    .service('HLDate', [function () {
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
    }])
    .service('HLText', [function() {
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
    }])
    .service('HLFilters', [function () {
        this.updateFilterQuery = function($scope) {
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
