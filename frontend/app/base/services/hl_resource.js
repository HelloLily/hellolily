angular.module('app.services').service('HLResource', HLResource);

HLResource.$inject = ['$injector'];
function HLResource($injector) {
    this.patch = (model, args, successTextOverride = null) => {
        return $injector.get(model).patch(args, () => {
            let modelText;

            if (successTextOverride) {
                modelText = successTextOverride;
            } else {
                // Split the model name by capital letters.
                // Join the split string with spaces.
                // Lowercase the whole string.
                modelText = model.split(/(?=[A-Z])/).join(' ').toLowerCase();
            }

            toastr.success(`The ${modelText} has been updated!`, 'Done');
        }, () => {
            toastr.error('Something went wrong while saving the field, please try again.', 'Oops!');
            // For now return an empty string, we'll implement proper errors later.
            return '';
        });
    };

    this.delete = (model, object) => {
        const regex = /(?=[A-Z])/g;
        const modelName = model.split(regex).join(' ').toLowerCase();

        return $injector.get(model).delete({id: object.id}).$promise.then(() => {
            toastr.success(`The ${modelName} has been deleted!`, 'Done');
        });
    };

    /**
     * Gets the options for the given field which can be used for selects.
     * @param model {string}: The model that's loaded.
     * @param field {string}: The field for which the values will be retrieved.
     *
     * @returns: values {Array}: The retrieved values.
     */
    this.getChoicesForField = (model, field) => {
        // Dynamically get resource.
        const resource = $injector.get(model);
        const convertedField = _convertVariableName(field);
        let choices;

        if (!resource.hasOwnProperty(convertedField)) {
            // Resource doesn't contain the given field.
            // So the field is probably a plural version of the given field or whatever.
            for (let key in resource) {
                if (key.indexOf(convertedField) > -1) {
                    choices = resource[key]();
                }
            }
        } else {
            // Call the proper endpoint/field.
            choices = resource[convertedField]();
        }

        return choices;
    };

    /**
     * Creates an object with the data the object will be patched with.
     * @param data: The changed data. Can be an object or just a value.
     * @param [field] {string}: What field the data will be set to.
     * @param [model] {Object}: The model from which data can be retrieved.
     *
     * @returns args {Object}: The data the object will be patched with.
     */
    this.createArgs = (data, field, model) => {
        let args;

        if (data && !Array.isArray(data) && typeof data === 'object') {
            args = data;
        } else {
            args = {
                id: model.id,
            };

            args[field] = data;
        }

        return args;
    };

    this.setSocialMediaFields = object => {
        if (object.social_media) {
            object.social_media.forEach(profile => {
                object[profile.name] = profile;
            });
        }
    };

    /**
     * Converts the given variable name so it can be used to retrieve a field of the given resource.
     * @param name {string}: The string that will be converted to camelCase.
     *
     * @returns {string}: The converted variable name.
     */
    function _convertVariableName(name) {
        const splitName = name.split('_');
        let convertedName = 'get';

        // Convert to title case.
        for (let i = 0; i < splitName.length; i++) {
            convertedName += splitName[i].charAt(0).toUpperCase() + splitName[i].slice(1);
        }

        return convertedName;
    }
}
