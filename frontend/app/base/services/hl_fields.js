angular.module('app.services').service('HLFields', HLFields);

function HLFields() {
    /**
     * cleanRelatedFields() cleans the related fields of the given objects
     * For now it only removes fields that have the is_deleted flag set to true
     *
     * @param object (object): the object to clean
     * @param model (string): contains the type of model
     *
     * @returns (object): returns the object with the related fields cleaned
     */
    this.cleanRelatedFields = function(object, model) {
        var relatedFields = ['email_addresses', 'phone_numbers', 'websites', 'addresses'];

        angular.forEach(object, function(fieldValues, field) {
            var cleanedValues = [];

            // We only want to clean the related fields, so check if the field is a related field
            if (relatedFields.indexOf(field) > -1) {
                // Loop through each array element
                angular.forEach(fieldValues, function(fieldValue) {
                    if (model === 'account' || (model === 'contact' && !fieldValue.hasOwnProperty('is_deleted'))) {
                        if (fieldValue.email_address) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.raw_input) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.city || fieldValue.postal_code || fieldValue.street || fieldValue.street_number) {
                            cleanedValues.push(fieldValue);
                        }

                        if (fieldValue.website) {
                            if (!fieldValue.is_primary || (fieldValue.is_primary && object.primaryWebsite)) {
                                cleanedValues.push(fieldValue);
                            }
                        }
                    }
                });

                object[field] = cleanedValues;
            }
        });

        return object;
    };

    this.addRelatedField = function(object, field) {
        switch (field) {
            case 'emailAddress':
                // Default status is 'Other'
                var status = 1;
                var isPrimary = false;

                if (object.email_addresses.length === 0) {
                    // No email addresses added yet, so first one is primary
                    status = 2;
                    isPrimary = true;
                }

                object.email_addresses.push({is_primary: isPrimary, status: status});
                break;
            case 'phoneNumber':
                object.phone_numbers.push({type: 'work'});
                break;
            case 'address':
                object.addresses.push({type: 'visiting'});
                break;
            case 'website':
                object.websites.push({website: '', is_primary: false});
                break;
            default:
                break;
        }
    };

    this.removeRelatedField = function(object, field, index, remove) {
        switch (field) {
            case 'emailAddress':
                object.email_addresses[index].is_deleted = remove;
                break;
            case 'phoneNumber':
                object.phone_numbers[index].is_deleted = remove;
                break;
            case 'address':
                object.addresses[index].is_deleted = remove;
                break;
            case 'website':
                index = object.websites.indexOf(index);
                if (index !== -1) {
                    object.websites[index].is_deleted = remove;
                }
                break;
            default:
                break;
        }
    };
}
