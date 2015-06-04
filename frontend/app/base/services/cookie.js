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
}
