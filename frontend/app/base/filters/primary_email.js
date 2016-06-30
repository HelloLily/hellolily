/**
 * primaryEmail takes the given email addresses and returns the email address
 * marked as 'Primary'.
 * If none exists it returns the first active email address.
 *
 * @param emailAddresses {Array}: Array containing the email addresses.
 *
 * @returns email_address {String}: The primary email address.
 */
angular.module('app.filters').filter('primaryEmail', primaryEmail);

primaryEmail.$inject = ['$filter'];
function primaryEmail($filter) {
    return function(emailAddresses) {
        var primaryEmailAddress = '';

        if (emailAddresses && emailAddresses.length) {
            primaryEmailAddress = $filter('filter')(emailAddresses, {status: 2})[0];

            if (!primaryEmailAddress) {
                // No primary email set, so just get the first active email address.
                primaryEmailAddress = $filter('filter')(emailAddresses, {status: '!' + 0})[0];
            }

            primaryEmailAddress = primaryEmailAddress.email_address;
        }

        return primaryEmailAddress;
    };
}
