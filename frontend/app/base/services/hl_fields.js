angular.module('app.services').service('HLFields', HLFields);

function HLFields () {
    /**
     * cleanRelatedFields() cleans the related fields of the given objects
     * For now it only removes fields that have the is_deleted flag set to true
     *
     * @param object (object): the object to clean
     *
     * @returns (object): returns the object with the related fields cleaned
     */
    this.cleanRelatedFields = function (object) {
        angular.forEach(object, function (fieldValues, field) {
            var cleanedValues = [];

            // We only want to clean the related fields, so check if the value is an array
            if (fieldValues instanceof Array && field != 'tags') {
                // Loop through each array element
                angular.forEach(fieldValues, function (fieldValue) {
                    if (!fieldValue.hasOwnProperty('is_deleted')) {
                        if (fieldValue.email_address) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.raw_input) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.city || fieldValue.postal_code ||
                                fieldValue.street || fieldValue.street_number) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.website) {
                            cleanedValues.push(fieldValue);
                        }
                    }
                });

                object[field] = cleanedValues;
            }

        });

        return object;
    };
}
