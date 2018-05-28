angular.module('app.utils.directives').directive('threadInfo', ThreadInfoDirective);

function ThreadInfoDirective() {
    return {
        restrict: 'E',
        scope: {
            messageType: '=',
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
        if (vm.messageType[0] === 1 ) {
            vm.action = 'reply';
            vm.nextMessage = vm.messageType[1];
        } else if (vm.messageType[0] === 2 ) {
            vm.action = 'reply-all';
            vm.nextMessage = vm.messageType[1];
        } else if (vm.messageType[0] === 3 ) {
            vm.action = 'forward';
            vm.nextMessage = vm.messageType[1];
        } else if (vm.messageType[0] === 4 ) {
            vm.action = 'reply-all fa-flip-horizontal';
            vm.nextMessage = vm.messageType[1];
        }
    }

    function gotoMessage() {
        $state.go('base.email.detail', {id: vm.nextMessage});
    }
}
