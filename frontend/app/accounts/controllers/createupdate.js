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
                templateUrl: 'accounts/controllers/form_outer.html',
                controller: AccountCreateController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        },
        resolve: {
            user: ['User', function (User) {
                return User.me().$promise;
            }]
        }
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/form_outer.html',
                controller: AccountCreateController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        },
        resolve: {
            user: ['User', function (User) {
                return User.me().$promise;
            }]
        }
    });
}

/**
 * Controller to create a new account.
 */
angular.module('app.accounts').controller('AccountCreateController', AccountCreateController);

AccountCreateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'User', 'HLFields', 'HLForms', 'user'];
function AccountCreateController($scope, $state, $stateParams, Account, User, HLFields, HLForms, user) {
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
    vm.currentUser = user;

    activate();

    ////

    function activate() {
        User.query().$promise.then(function (userList) {
            angular.forEach(userList, function (user) {
                vm.people.push({
                    id: user.id,
                    // Convert to single string so searching with spaces becomes possible
                    name: _getFullName(user)
                });
            });
        });

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

                if(vm.account.tags.length){
                    var tags = [];
                    angular.forEach(account.tags, function (tag){
                        tags.push(tag.name);
                    });
                    vm.account.tags = tags;
                }

                $scope.conf.pageTitleBig = vm.account.name;

                if (vm.account.assigned_to) {
                    // .name is used in the template, so set that property
                    vm.account.assigned_to.name = _getFullName(vm.account.assigned_to);
                }
            });
        } else {
            $scope.conf.pageTitleBig = 'New account';
            vm.account = Account.create();
            vm.account.assigned_to = vm.currentUser.id;
        }
    }

    function _getFullName(user) {
        // $.grep removes values that are empty so the .join doesn't have double spaces
        return $.grep([user.first_name, user.preposition, user.last_name], Boolean).join(' ');
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

    function saveAccount(form) {
        HLForms.blockUI();

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
        if (typeof vm.account.assigned_to === 'object' && vm.account.assigned_to && vm.account.assigned_to.id) {
            vm.account.assigned_to = vm.account.assigned_to.id;
        }

        if (vm.account.tags && vm.account.tags.length) {
            var tags = [];
            angular.forEach(vm.account.tags, function (tag) {
                if (tag) {
                    tags.push({name: (tag.name) ? tag.name : tag});
                }

                vm.account.tags = tags;
            });
        }

        // Clear all errors of the form (in case of new errors)
        angular.forEach(form, function(value, key) {
            if (typeof value === 'object' && value.hasOwnProperty('$modelValue')) {
                form[key].$error = {};
                form[key].$setValidity(key, true);
            }
        });

        if (vm.account.id) {
            // If there's an ID set it means we're dealing with an existing account, so update it
            vm.account.$update(function () {
                toastr.success('I\'ve updated the account for you!', 'Done');
                $state.go('base.accounts.detail', {id: vm.account.id}, {reload:true});
            }, function (response) {
                _handleBadResponse(response, form);
            })
        }
        else {
            vm.account = HLFields.cleanRelatedFields(vm.account);

            vm.account.$save(function () {
                toastr.success('Yup, I\'ve got it', 'Saved');
                $state.go('base.accounts.detail', {id: vm.account.id});
            }, function (response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        // Set error of the first website as the primary website error
        if (vm.account.primaryWebsite && response.data['websites'] && response.data['websites'].length) {
            response.data['primaryWebsite'] = response.data['websites'].shift()['website'];
        }

        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }
}
