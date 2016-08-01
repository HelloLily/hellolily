angular.module('app.services').factory('HLMessages', HLMessages);

HLMessages.$inject = [];
function HLMessages() {
    return {
        contact: {
            accountInfoTooltip: 'I\'ve loaded the selected account\'s data for you. Now you don\'t have to enter duplicate data!',
            accountListInfoTooltip: 'This is the data of the account(s) the contact works for',
            contactInfoTooltip: 'This is the current contact\'s data',
        },
        alerts: {
            accountForm: {
                title: 'Website already exists',
                body: 'This website has already been added to an existing account: <br />' +
                '<strong>%(account)s</strong><br />' +
                'Are you sure you want to use:<br />' +
                '%(website)s',
                cancelButtonText: 'No, clear the field',
            },
            delete: {
                confirmTitle: 'Are you sure?',
                confirmText: 'You are about to delete <strong>%(name)s</strong>.<br />You won\'t be able to revert this!',
                confirmButtonText: 'Yes, delete it!',
                successTitle: 'Deleted',
                successText: 'The %(model)s <strong>%(name)s</strong> has been deleted.',
                errorTitle: 'Error',
                errorText: 'There was an error processing your request.<br />Please try again.',
            },
            assignTo: {
                questionText: 'Assign this case to yourself?',
            },
        },
    };
}

