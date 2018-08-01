angular.module('app.email.services').factory('EmailAddress', EmailAddress);

function EmailAddress() {
    var _emailAddress = {};

    _emailAddress.checkValidityOfEmailList = checkValidityOfEmailList;
    _emailAddress.checkValidityOfEmail = checkValidityOfEmail;

    //////

    /**
     *
     * Function to check if a email address is valid.
     *
     * @param recipients comma separated or single string of addresses to check
     * @returns {Array} of invalid email addresses
     */
    function checkValidityOfEmailList(recipients) {
        var invalidAddress = [];
        var recipientsList = [];

        if (!recipients) {
            return invalidAddress;
        }

        recipientsList = recipients.split(',');
        recipientsList.forEach(function(recipient) {
            var email;
            var emailRegex;
            var matches;
            var isValid;
            var splitRecipient;

            if (recipient !== '') {
                splitRecipient = recipient.split('" ');
                email = splitRecipient[splitRecipient.length - 1];

                if (splitRecipient.length > 1) {
                    emailRegex = /<(.*?)>/gi;
                    matches = emailRegex.exec(splitRecipient[splitRecipient.length - 1]);
                    if (matches.length > 0) {
                        email = matches[1];
                    }
                }

                isValid = checkValidityOfEmail(email);
                if (!isValid) {
                    invalidAddress.push(email);
                }
            }
        });

        return invalidAddress;
    }

    /**
     * rfc822 complaint email address checker
     *
     * @param emailAddress
     * @returns {boolean}
     */
    function checkValidityOfEmail(emailAddress) {
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(emailAddress);
    }

    return _emailAddress;
}
