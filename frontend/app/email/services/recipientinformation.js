angular.module('app.email.services').factory('RecipientInformation', RecipientInformation);

RecipientInformation.$inject = ['$http'];
function RecipientInformation ($http) {

    var RecipientInformation = {};

    RecipientInformation.getInformation = getInformation;

    //////

    function getInformation(recipients) {
        recipients.forEach(function (recipient) {
            // If there's a name set, try to get the contact id
            // Don't set/change the name because we want to keep the original email intact
            if (recipient.name != '') {
                $http.get('/search/emailaddress/' + recipient.email_address)
                    .success(function (data) {
                        if (data.type == 'contact') {
                            if (data.data.id) {
                                recipient.contact_id = data.data.id;
                            }
                        }
                    });
            }
        });
    }

    return RecipientInformation;
}
