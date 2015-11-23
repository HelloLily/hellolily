angular.module('app.dashboard').controller('WidgetSettingsModal', WidgetSettingsModalController);

WidgetSettingsModalController.$inject = ['$modalInstance', 'LocalStorage'];
function WidgetSettingsModalController($modalInstance, LocalStorage) {
    var vm = this;
    var storage = LocalStorage('widgetInfo');

    vm.widgetSettings = storage.get('', {});

    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    ////////////

    function saveModal() {
        // Store the widget settings
        storage.put('', vm.widgetSettings);

        $modalInstance.close();
    }

    function closeModal() {
        $modalInstance.dismiss();
    }
}
