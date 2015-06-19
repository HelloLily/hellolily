/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/form.html',
                controller: AccountCreateController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/form.html',
                controller: AccountCreateController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });
}

/**
 * Controller to create a new account.
 */
angular.module('app.accounts').controller('AccountCreateController', AccountCreateController);

AccountCreateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'User', 'HLFields'];
function AccountCreateController($scope, $state, $stateParams, Account, User, HLFields) {
    var vm = this;
    vm.account = {};
    vm.people = [];
    vm.tags = [];
    vm.errors = {
        name: []
    };

    vm.loadDataproviderData = loadDataproviderData;
    vm.saveAccount = saveAccount;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;

    activate();

    ////

    function activate() {
        vm.people = User.query();
        $scope.conf.pageTitleSmall = 'change is natural';

        _getAccount();
    }

    function _getAccount() {
        // Fetch the account or create empty account
        if ($stateParams.id) {
            $scope.conf.pageTitleBig = 'Edit account';
            Account.get({id: $stateParams.id}).$promise.then(function (account) {
                vm.account = account;
                angular.forEach(account.websites, function (website) {
                    if (website.is_primary) {
                        vm.account.primaryWebsite = website.website;
                    }
                });
                if (!vm.account.primaryWebsite || vm.account.primaryWebsite == '') {
                    vm.account.primaryWebsite = '';
                }
                $scope.conf.pageTitleBig = vm.account.name;
            });
        } else {
            $scope.conf.pageTitleBig = 'New account';
            vm.account = Account.create();
        }
    }

    function loadDataproviderData(form) {
        toastr.info('Running around the world to fetch info', 'Here we go');
        vm.account.getDataproviderInfo(form.primaryWebsite.$modelValue).then(function () {
            toastr.success('Got it!', 'Whoohoo');
        }, function () {
            toastr.error('I couldn\'t find any data', 'Sorry');
        });
    }

    function addRelatedField(field) {
        vm.account.addRelatedField(field);
    }

    function removeRelatedField(field, index, remove) {
        vm.account.removeRelatedField(field, index, remove);
    }

    function saveAccount() {
        var primaryWebsite = vm.account.primaryWebsite;

        // Make sure it's not an empty website being added
        if (primaryWebsite && primaryWebsite != 'http://' && primaryWebsite != 'https://') {
            var exists = false;
            for (var i in vm.account.websites) {
                if (vm.account.websites[i].website == primaryWebsite) {
                    exists = true;
                    vm.account.websites[i].is_primary = true;
                    break;
                }
            }
            if (!exists) {
                vm.account.websites.push({website: primaryWebsite, is_primary: true})
            }
        }

        // If the account is edited and the assigned to isn't changed, it's an object
        // So if that's the case get the id and set 'assigned_to' to that value
        if (typeof vm.account.assigned_to === 'object') {
            vm.account.assigned_to = vm.account.assigned_to.id;
        }

        if (vm.account.id) {
            vm.account.$update(function () {
                toastr.success('I\'ve updated the account for you!', 'Done');
                $state.go('base.accounts.detail', {id: vm.account.id});
            }, function (response) {
                toastr.error('Uh oh, there seems to be a problem' + getErrors(response.data), 'Error');
            })
        }
        else {
            vm.account = HLFields.cleanRelatedFields(vm.account);

            vm.account.$save(function () {
                toastr.success('Yup, I\'ve got it', 'Saved');
                $state.go('base.accounts.detail', {id: vm.account.id});
            }, function (response) {
                toastr.error('Uh oh, there seems to be a problem' + getErrors(response.data), 'Error');
            })
        }

        function getErrors(data) {
            // TODO: Simple error display for now, fix in LILY-951
            var errors = '<br><br> The following fields returned an error:';

            for (var field in data) {
                var field_name = field.charAt(0).toUpperCase() + field.slice(1);
                field_name = field_name.replace('_', ' ');
                var error_field_string = '<br><strong>' + field_name + '</strong>: ';

                if (data[field] instanceof Array) {
                    data[field].forEach(function (field_value) {
                        if (typeof field_value === 'object') {
                            for (var key in field_value) {
                                errors += error_field_string + field_value[key][0];
                            }
                        }
                        else {
                            errors += error_field_string + data[field][0];
                        }
                    });
                }
            }

            return errors
        }
    }
}
