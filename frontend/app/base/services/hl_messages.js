angular.module('app.services').factory('HLMessages', HLMessages);

HLMessages.$inject = [];
function HLMessages() {
    return {
        contact: {
            accountInfoTooltip: 'I\'ve loaded the selected account\'s data for you. Now you don\'t have to enter duplicate data!',
            contactInfoTooltip: 'This is the current contact\'s data',
        },
    };
}

