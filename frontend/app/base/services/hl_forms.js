angular.module('app.services').service('HLForms', HLForms);

function HLForms () {
    /**
     * setErrors() sets the errors of the forms, making use of Angular's error handling.
     *
     * @param form (object): the form on which the errors are set
     * @param data (object): object containing all the errors
     *
     */
    this.setErrors = function(form, data) {
        // Unblock the UI so user can retry filling in the form
        Metronic.unblockUI();

        // We don't want to continue if the returned errors aren't properly formatted
        if (typeof data === 'object') {
            for (var field in data) {
                // Errors are always in the <field>: Array format, so iterate over the array
                for (var i = 0; i < data[field].length; i++) {
                    // Related fields are always an object, so check for that
                    if (typeof data[field][i] === 'object') {
                        for (var key in data[field][i]) {
                            var formField = [field, key, i].join('-');

                            // The error is always the first element, so get it and set as the error message
                            form[formField].$error = {message: data[field][i][key][0]};
                            form[formField].$setValidity(formField, false);
                        }
                    } else {
                        // Not a related field, so get the error and set validity to false
                        form[field].$error = {message: data[field][0]};
                        form[field].$setValidity(field, false);
                    }
                }
            }
        }
    };

    /**
     * Block the UI, giving the user feedback about te form.
     */
    this.blockUI = function() {
        // animate shows a CSS animation instead of the standard 'Loading' text
        Metronic.blockUI({animate: true});
    };
}
