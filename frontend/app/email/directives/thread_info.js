angular.module('app.utils.directives').directive('threadInfo', ThreadInfoDirective);

function ThreadInfoDirective() {
    return {
        restrict: 'E',
        scope: {
            messageType: '=',
            messageTypeToId: '=',
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
        vm.action = 'nothing';
        if (vm.messageType === 1 ) {
            vm.action = 'reply';
            vm.nextMessage = vm.messageTypeToId;
        } else if (vm.messageType === 2 ) {
            vm.action = 'reply-all';
            vm.nextMessage = vm.messageTypeToId;
        } else if (vm.messageType === 3 ) {
            vm.action = 'forward';
            vm.nextMessage = vm.messageTypeToId;
        } else if (vm.messageType === 4 ) {
            vm.action = 'reply-all fa-flip-horizontal';
            vm.nextMessage = vm.messageTypeToId;
        }
    }

    function gotoMessage() {
        $state.go('base.email.detail', {id: vm.nextMessage});
    }
}
