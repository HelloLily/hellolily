angular.module('app.dashboard').controller('WidgetSettingsModal', WidgetSettingsModalController);

WidgetSettingsModalController.$inject = ['$uibModalInstance', 'LocalStorage'];
function WidgetSettingsModalController($uibModalInstance, LocalStorage) {
    var vm = this;
    var storage = LocalStorage('widgetInfo');

    vm.widgetSettings = storage.get('', {});

    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    ////////////

    function saveModal() {
        // Store the widget settings
        storage.put('', vm.widgetSettings);

        $uibModalInstance.close();
    }

    function closeModal() {
        $uibModalInstance.dismiss();
    }
}
