angular.module('app.services').service('HLForms', HLForms);

function HLForms() {
    /**
     * setErrors() sets the errors of the forms, making use of Angular's error handling.
     *
     * @param form (object): the form on which the errors are set
     * @param data (object): object containing all the errors
     *
     */
    this.setErrors = function(form, data) {
        // Unblock the UI so user can retry filling in the form.
        Metronic.unblockUI();

        // We don't want to continue if the returned errors aren't properly formatted.
        if (typeof data === 'object') {
            for (var field in data) {
                // Errors are always in the <field>: Array format, so iterate over the array.
                for (var i = 0; i < data[field].length; i++) {
                    // Related fields are always an object, so check for that.
                    if (typeof data[field][i] === 'object') {
                        for (var key in data[field][i]) {
                            var formField = [field, key, i].join('-');

                            // The error is always the first element, so get it and set as the error message.
                            form[formField].$error = {message: data[field][i][key][0]};
                            form[formField].$setValidity(formField, false);
                        }
                    } else {
                        // Not a related field, so get the error and set validity to false.
                        form[field].$error = {message: data[field][0]};
                        form[field].$setValidity(field, false);
                    }
                }
            }
        }
    };

    /**
     * Clear all errors of the form (in case of new errors).
     * @param form
     */
    this.clearErrors = function(form) {
        angular.forEach(form, function(value, key) {
            if (typeof value === 'object' && value.hasOwnProperty('$modelValue')) {
                form[key].$error = {};
                form[key].$setValidity(key, true);
            }
        });
    };

    /**
     * Clean the fields of the given view model.
     * @param viewModel (object): The view model that's being created/updated.
     */
    this.clean = function(viewModel) {
        angular.forEach(viewModel, function(fieldValue, field) {
            if (fieldValue) {
                // We don't want to send whole objects to the API, because they're not accepted.
                // So loop through all fields and extract IDs.
                if (fieldValue.constructor === Array) {
                    var ids = [];

                    angular.forEach(fieldValue, function(item) {
                        if (typeof item === 'object') {
                            if (item.hasOwnProperty('id')) {
                                ids.push(item.id);
                            }
                        } else if (typeof item === 'number') {
                            // Seems to be an ID, so just add it to the ID array.
                            ids.push(item);
                        }
                    });

                    viewModel[field] = ids;
                } else if (typeof fieldValue === 'object') {
                    if (fieldValue.hasOwnProperty('id')) {
                        viewModel[field] = fieldValue.id;
                    } else if (fieldValue.hasOwnProperty('value')) {
                        viewModel[field] = fieldValue.value;
                    }
                }
            }
        });

        return viewModel;
    };

    /**
     * Block the UI, giving the user feedback about the form.
     */
    this.blockUI = function() {
        // animate shows a CSS animation instead of the standard 'Loading' text.
        Metronic.blockUI({animate: true});
    };
}
