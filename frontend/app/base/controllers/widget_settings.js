angular.module('app.dashboard').controller('WidgetSettingsModal', WidgetSettingsModalController);

WidgetSettingsModalController.$inject = ['$state', '$uibModalInstance', 'LocalStorage'];
function WidgetSettingsModalController($state, $uibModalInstance, LocalStorage) {
    var vm = this;
    var storage = new LocalStorage($state.current.name + 'widgetInfo');

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
