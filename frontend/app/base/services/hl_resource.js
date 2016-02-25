angular.module('app.services').service('HLResource', HLResource);

HLResource.$inject = ['$injector'];
function HLResource($injector) {
    this.patch = function(model, args) {
        return $injector.get(model).patch(args, function() {
            toastr.success('I\'ve updated the ' + model.toLowerCase() + ' for you!', 'Done');
        }, function() {
            toastr.error('Something went wrong while saving the field, please try again.', 'Oops!');
            // For now return an empty string, we'll implement proper errors later.
            return '';
        });
    };

    /**
     * Gets the options for the given field which can be used for selects.
     * @param model {string}: The model that's loaded.
     * @param field {string}: The field for which the values will be retrieved.
     *
     * @returns: values {Array}: The retrieved values.
     */
    this.getChoicesForField = function(model, field) {
        // Dynamically get resource.
        var resource = $injector.get(model);

        field = _convertVariableName(field);

        if (!resource.hasOwnProperty(field)) {
            // Resource doesn't contain the given field.
            // So the field is probably a plural version of the given field or whatever.
            for (var key in resource) {
                if (key.indexOf(field) > -1) {
                    return resource[key]();
                }
            }
        } else {
            // Call the proper endpoint/field.
            return resource[field]();
        }
    };

    /**
     * Converts the given variable name so it can be used to retrieve a field of the given resource.
     * @param name {string}: The string that will be converted to camelCase.
     *
     * @returns {string}: The converted variable name.
     */
    function _convertVariableName(name) {
        var splitName = name.split('_');
        var convertedName = 'get';

        // Convert to title case.
        for (var i = 0; i < splitName.length; i++) {
            convertedName += splitName[i].charAt(0).toUpperCase() + splitName[i].slice(1);
        }

        return convertedName;
    }
}
