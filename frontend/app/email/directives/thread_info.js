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
            vm.action = history.action;
            if (history.action === 'forward-multi') {
                vm.action = 'reply-all fa-flip-horizontal';
            }

            if (history.action_message_id) {
                vm.actionMessageId = history.action_message_id;
            }
        });
    }

    function gotoMessage() {
        $state.go('base.email.detail', {id: vm.actionMessageId});
    }
}
