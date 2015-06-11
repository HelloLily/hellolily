angular.module('app.email.services').factory('SelectedEmailAccount', SelectedEmailAccount);

function SelectedEmailAccount () {

    var factory = {
        currentAccountId: null,
        setCurrentAccountId: setCurrentAccountId,
        currentFolderId: null,
        setCurrentFolderId: setCurrentFolderId
    };
    return factory;

    function setCurrentAccountId (accountId) {
        factory.currentAccountId = accountId;
    }

    function setCurrentFolderId (folderId) {
        factory.currentFolderId = folderId;
    }
}
