angular.module('app.dashboard').controller('WidgetSettingsModal', WidgetSettingsModalController);

WidgetSettingsModalController.$inject = ['$modalInstance', 'Cookie'];
function WidgetSettingsModalController ($modalInstance, Cookie) {
    var vm = this;
    var cookie = Cookie('widgetInfo');

    vm.widgetSettings = cookie.get('', {});

    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    ////////////

    function saveModal() {
        cookie.put('', vm.widgetSettings);

        $modalInstance.close();
    }

    function closeModal() {
        $modalInstance.dismiss();
    }
}
