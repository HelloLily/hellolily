angular.module('app.utils.directives').directive('threadInfo', ThreadInfoDirective);

function ThreadInfoDirective() {
    return {
        restrict: 'E',
        scope: {
            messageId: '=',
        },
        controller: ThreadInfoController,
        controllerAs: 'vm',
        bindToController: true,
        templateUrl: 'email/directives/thread_info.html',
    };
}

ThreadInfoController.$inject = ['$state', 'EmailMessage'];
function ThreadInfoController($state, EmailMessage) {
    var vm = this;
    vm.action = '';
    vm.nextMessage = null;

    vm.gotoMessage = gotoMessage;

    activate();

    ////

    function activate() {
        EmailMessage.history({id: vm.messageId}, function(history) {
            vm.action = 'nothing';
            if (history.replied_with) {
                vm.action = _getEmailAddresses(history.replied_with).length === 1 ? 'reply' : 'reply-all';
                vm.nextMessage = history.replied_with;
            } else if (history.forwarded_with) {
                if (_getEmailAddresses(history.replied_with).length === 1) {
                    vm.action = 'forward';
                } else {
                    // hack, there is no forward all
                    vm.action = 'reply-all fa-flip-horizontal';
                }
                vm.nextMessage = history.forwarded_with;
            }
        });
    }

    function _getEmailAddresses(message) {
        var emailAddresses = [];

        // TODO: LILY-982: Fix empty messages being sent
        if (message) {
            if (message.received_by_email) {
                emailAddresses = emailAddresses.concat(message.received_by_email);
            }

            if (message.received_by_cc_email) {
                emailAddresses = emailAddresses.concat(message.received_by_cc_email);
            }
        }

        return emailAddresses;
    }

    function gotoMessage() {
        $state.go('base.email.detail', {id: vm.nextMessage.id});
    }
}
