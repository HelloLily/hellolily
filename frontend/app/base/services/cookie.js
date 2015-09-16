/**
 * Cookie Service provides a simple interface to get and store cookie values
 *
 * Set `prefix` to give cookie keys a prefix
 */
angular.module('app.services').service('Cookie', Cookie);

Cookie.$inject = ['$cookieStore'];
function Cookie ($cookieStore) {
    function CookieFactory (prefix) {
        return new Cookie(prefix);
    }

    function Cookie(prefix) {
        this.prefix = prefix;
    }

    /**
     * Try to retrieve and return a value from the cookie or
     * returns a default value if cookie doesn't exist.
     *
     * @param field {string}: Name of the field to retrieve info from
     * @param defaultValue {*} : Default value when cookie doesn't exist
     * @returns {*}: Retrieved or default value
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
     * Try to retrieve and return an object from the cookie or
     * returns a default value if cookie doesn't exist.
     *
     * @param field {string}: Name of the field to retrieve info from
     * @param defaultValue {*} : Default value when cookie doesn't exist
     * @returns {*}: Retrieved or default value
     */
    Cookie.prototype.getObjectValue = function (field, defaultValue) {
        try {
            var values = $cookieStore.get(this.prefix);
            var value = values[field];

            return (value !== undefined) ? value : defaultValue;
        } catch (error) {
            $cookieStore.remove(this.prefix[field]);
            return defaultValue;
        }
    };

    /**
     * Creates/updates a cookie based on the given prefix + field name.
     *
     * @param field {string}: Name of the field to be created/updated
     * @param value {*} : The value of the cookie
     */
    Cookie.prototype.put = function (field, value) {
        $cookieStore.put(this.prefix + field, value);
    };

    /**
     * Stores an object as a cookie instead of creating a cookie for every option.
     * @param field {string}: Name of the field to be created/updated
     * @param value {*} : The value of the cookie
     */
    Cookie.prototype.putObjectValue = function (field, value) {
        var values = this.get('', {});
        values[field] = value;

        $cookieStore.put(this.prefix, values);
    };

    return CookieFactory;
}
