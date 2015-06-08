angular.module('app.email.services').factory('SelectedEmailAccount', SelectedEmailAccount);

function SelectedEmailAccount () {

    var factory = {
        currentAccountId: null,
        setCurrentAccountId: setCurrentAccountId
    };
    return factory;

    function setCurrentAccountId (accountId) {
        factory.currentAccountId = accountId;
    }
}
