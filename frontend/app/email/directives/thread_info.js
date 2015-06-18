angular.module('app.utils.directives').directive('threadInfo', ThreadInfoDirective);

function ThreadInfoDirective() {
    return {
        restrict: 'E',
        scope: {
            messageId:'='
        },
        controller: ThreadInfoController,
        controllerAs: 'vm',
        bindToController: true,
        templateUrl: 'email/directives/thread_info.html'
    };
}

ThreadInfoController.$inject = ['$state', 'EmailMessage'];
function ThreadInfoController ($state, EmailMessage) {
    var vm = this;
    vm.action = '';
    vm.nextMessage = null;

    vm.gotoMessage = gotoMessage;

    activate();

    ////

    function activate () {
        EmailMessage.history({id: vm.messageId}, function(history) {
            if (history.replied_with) {
                vm.action = _getEmailAddresses(history.replied_with).length == 1 ? 'reply' : 'reply-all';
                vm.nextMessage = history.replied_with;
            } else if(history.forwarded_with) {
                vm.action = 'forward';
                vm.nextMessage = history.forwarded_with;
            } else {
                vm.action = 'nothing';
            }
        });
    }

    function _getEmailAddresses (message) {
        var emailAddresses = [];
        if (message.received_by_email) {
            emailAddresses = emailAddresses.concat(message.received_by_email);
        }
        if (message.received_by_cc_email) {
            emailAddresses = emailAddresses.concat(message.received_by_email);
        }
        return emailAddresses;
    }

    function gotoMessage () {
        $state.go('base.email.detail', {id: vm.nextMessage.id});
    }
}
