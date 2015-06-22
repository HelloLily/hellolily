angular.module('app.services').service('HLObjectDetails', HLObjectDetails);
function HLObjectDetails () {
    this.getPhone = function (object) {
        if (object.phone_mobile) return object.phone_mobile[0];
        if (object.phone_work) return object.phone_work[0];
        if (object.phone_other) return object.phone_other[0];

        return null;
    };

    this.getPhones = function (object) {
        var phones = [];

        if (object.phone_mobile) phones = phones.concat(object.phone_mobile);
        if (object.phone_work) phones = phones.concat(object.phone_work);
        if (object.phone_other) phones = phones.concat(object.phone_other);

        return phones;
    };

    this.getEmailAddresses = function (object) {
        var email_addresses = object.email_addresses;

        if (email_addresses.length > 1) {
            // Copy the email address array and loop over it
            angular.forEach(email_addresses.slice(), function (email_address, index) {
                // Check if email address has the status 'Primary'
                if (email_address.status == 2) {
                    // Remove element at specified index
                    email_addresses.splice(index, 1);
                    // Add the email address to the start of the array
                    email_addresses.unshift(email_address);
                }
            });
        }

        return email_addresses;
    };
}
