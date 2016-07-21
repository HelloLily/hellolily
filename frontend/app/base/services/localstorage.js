/**
 * LocalStorage Service provides a simple interface to get and store local storage values
 *
 * Set `prefix` to give local storage keys a prefix
 */
angular.module('app.services').service('LocalStorage', LocalStorageService);

LocalStorageService.$inject = [];
function LocalStorageService() {
    function LocalStorageFactory(prefix) {
        return new LocalStorage(prefix);
    }

    function LocalStorage(prefix) {
        this.prefix = prefix;
    }

    /**
     * Try to retrieve and return a value from the local storage or
     * returns a default value if local storage doesn't exist.
     *
     * @param field {string}: Name of the field to retrieve info from
     * @param defaultValue {*} : Default value when locally stored doesn't exist
     * @returns {*}: Retrieved or default value
     */
    LocalStorage.prototype.get = function(field, defaultValue) {
        var value = localStorage.getItem(this.prefix + field);

        try {
            value = JSON.parse(value);

            return (value !== null) ? value : defaultValue;
        } catch (error) {
            localStorage.removeItem(this.prefix + field);
            return defaultValue;
        }
    };

    /**
     * Try to retrieve and return an object from the local storage or
     * returns a default value if local storage doesn't exist.
     *
     * @param field {string}: Name of the field to retrieve info from
     * @param defaultValue {*} : Default value when local storage doesn't exist
     * @returns {*}: Retrieved or default value
     */
    LocalStorage.prototype.getObjectValue = function(field, defaultValue) {
        var storage;
        var values;
        var value;

        try {
            storage = this;
            values = storage.get('', defaultValue);
            value = values[field];

            return value ? value : defaultValue;
        } catch (error) {
            localStorage.removeItem(this.prefix[field]);
            return defaultValue;
        }
    };

    /**
     * Creates/updates a local storage based on the given prefix + field name.
     *
     * @param field {string}: Name of the field to be created/updated
     * @param value {*} : The value to be stored
     */
    LocalStorage.prototype.put = function(field, value) {
        var convertedValue = JSON.stringify(value);

        localStorage.setItem(this.prefix + field, convertedValue);
    };

    /**
     * Stores an object as a local storage instead of creating a local storage for every option.
     * @param field {string}: Name of the field to be created/updated
     * @param value {*} : The value of the local storage
     */
    LocalStorage.prototype.putObjectValue = function(field, value) {
        var storage = this;
        var values = storage.get('', {});
        values[field] = value;

        localStorage.setItem(this.prefix, JSON.stringify(values));
    };

    return LocalStorageFactory;
}
