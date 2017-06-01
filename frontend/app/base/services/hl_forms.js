angular.module('app.services').service('HLForms', HLForms);

HLForms.$inject = ['$timeout'];
function HLForms($timeout) {
    /**
     * setErrors() sets the errors of the forms, making use of Angular's error handling.
     *
     * @param form (object): the form on which the errors are set
     * @param data (object): object containing all the errors
     *
     */
    this.setErrors = (form, data) => {
        // Unblock the UI so user can retry filling in the form.
        Metronic.unblockUI();

        // We don't want to continue if the returned errors aren't properly formatted.
        if (typeof data === 'object') {
            for (let field in data) {
                // Errors are always in the <field>: Array format, so iterate over the array.
                for (let i = 0; i < data[field].length; i++) {
                    // Related fields are always an object, so check for that.
                    if (typeof data[field][i] === 'object') {
                        for (let key in data[field][i]) {
                            const formField = [field, key, i].join('-');

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

            $timeout(() => {
                angular.element('.form-control.ng-invalid:first').focus();
            });
        }
    };

    /**
     * Clear all errors of the form (in case of new errors).
     * @param form (object): The form from which the errors should be cleared.
     */
    this.clearErrors = form => {
        angular.forEach(form, (value, key) => {
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
    this.clean = viewModel => {
        // We don't want to clean certain fields.
        const ignoredFields = ['tags'];

        angular.forEach(viewModel, (fieldValue, field) => {
            if (ignoredFields.indexOf(field) < 0 && fieldValue) {
                // We don't want to send whole objects to the API, because they're not accepted.
                // So loop through all fields and extract IDs.
                if (fieldValue.constructor === Array) {
                    let ids = [];

                    angular.forEach(fieldValue, item => {
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
    this.blockUI = () => {
        // Animate shows a CSS animation instead of the standard 'Loading' text.
        Metronic.blockUI({animate: true});
    };

    this.unblockUI = () => {
        Metronic.unblockUI();
    };
}
