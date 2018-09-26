const Uppy = require('@uppy/core');
const Dashboard = require('@uppy/dashboard');
const XHRUpload = require('@uppy/xhr-upload');

angular.module('app.utils.directives').directive('objectFiles', objectFiles);

function objectFiles() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
        },
        templateUrl: 'objectfiles/directives/object_files.html',
        controller: ObjectFilesController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

ObjectFilesController.$inject = ['$scope', '$cookies', '$window'];
function ObjectFilesController($scope, $cookies, $window) {
    const vm = this;
    const uppy = new Uppy({
        restrictions: {
            maxFileSize: 5000000,
            maxNumberOfFiles: 5,
        },
    }).use(Dashboard).use(XHRUpload, {
        endpoint: '/api/files/',
        fieldName: 'file',
        headers: {
            'X-CSRFToken': $cookies.get('csrftoken'),
        },
    });

    vm.currentUser = currentUser;

    vm.openModal = openModal;
    vm.removeFromList = removeFromList;

    uppy.on('file-added', file => {
        uppy.setFileMeta(file.id, {
            gfk_content_type: vm.object.content_type.id,
            gfk_object_id: vm.object.id,
            size: file.size,
            user: currentUser.id,
        });
    });

    uppy.on('upload-success', (file, body) => {
        $window.location.reload();
    });

    function openModal() {
        uppy.getPlugin('Dashboard').openModal();
    }

    function removeFromList(file) {
        const index = vm.object.files.indexOf(file);
        vm.object.files.splice(index, 1);
        $scope.$apply();
    }
}
