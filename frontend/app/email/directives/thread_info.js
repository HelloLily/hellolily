angular.module('app.utils.directives').directive('threadInfo', ThreadInfoDirective);

function ThreadInfoDirective() {
    return {
        restrict: 'E',
        scope: {
            message: '=',
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
        const accountEmail = vm.message.account.email_address;
        const sentFromAccount = (accountEmail === vm.message.sender.email_address);

        if (sentFromAccount) {
            // Current email message is send by the user and therefore not a possible reply or forwarded email message.
            return;
        }

        const searchParams = {
            thread: vm.message.thread_id,
            sort: 'sent_date',
            size: 100,
        };
        EmailMessage.search(searchParams, data => {
            vm.action = 'nothing';

            let thread = data.hits;

            // Lookup index of the email in the thread.
            let index;
            for (index = 0; index < thread.length; index++) {
                if (vm.message.id === thread[index].id) {
                    break;
                }
            }

            if (index === undefined) {
                // Possible when thread is larger than paging size.
                return;
            }

            // Only look at the thread after the current mail.
            thread = thread.slice(index + 1);
            if (thread.length === 0) {
                // Current email message is the last in the thread.
                return;
            }

            // The current email message isn't the last in the thread. So look the follow up messages in the thread to
            // determine what actions occured on the current email message. Current email message is not send from the
            // account of the user, so it is a received email message. So determine if we replied or forwarded it.

            // Get all the outgoing follow up messages in the thread.
            for (let i = thread.length - 1; i >= 0; i--) {
                if (thread[i].sender.email_address !== accountEmail) {
                    // So remove messages from the thread where current user isn't the sender.
                    thread.splice(i, 1);
                }
            }
            if (thread.length === 0) {
                return;
            }

            // We only need to look at the first follow up message in the thread.
            const nextMessage = thread[0];
            const emailAddresses = _getEmailAddresses(nextMessage);

            if (nextMessage.subject.startsWith('Re: ')) {
                vm.action = emailAddresses.length === 1 ? 'reply' : 'reply-all';
            } else if (nextMessage.subject.startsWith('Fwd: ')) {
                vm.action = emailAddresses.length === 1 ? 'forward' : 'reply-all fa-flip-horizontal';
            }
            vm.nextMessage = nextMessage;
        });
    }

    function _getEmailAddresses(message) {
        const emailAddresses = [];

        // TODO: LILY-982: Fix empty messages being sent.
        if (message) {
            message.received_by.forEach(item => {
                emailAddresses.push(item.email_address);
            });
            message.received_by_cc.forEach(item => {
                emailAddresses.push(item.email_address);
            });
        }

        // Remove duplicates before returning.
        return [...new Set(emailAddresses)];
    }

    function gotoMessage() {
        $state.go('base.email.detail', {id: vm.nextMessage.id});
    }
}
