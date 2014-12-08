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
    }]);
