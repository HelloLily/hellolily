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

        recipientsList = recipientsList.split(',');
        recipientsList.forEach(function(recipient) {
            if (recipient !== '') {
                recipient = recipient.split('" ');
                var email = recipient[recipient.length - 1];

                if (recipient.length > 1) {
                    var emailRegex = /<(.*?)>/gi;
                    var matches = emailRegex.exec(recipient[recipient.length - 1]);
                    if (matches.length > 0) {
                        email = matches[1];
                    }
                }

                var isValid = checkValidityOfEmail(email);
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
    function checkValidityOfEmail(emailAddress){
        return /^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$/.test(emailAddress);
    }

    return _emailAddress;
}
