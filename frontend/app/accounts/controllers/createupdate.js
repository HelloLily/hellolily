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
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/form.html',
                controller: AccountCreateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit',
        },
    });
}

/**
 * Controller to create a new account.
 */
angular.module('app.accounts').controller('AccountCreateController', AccountCreateController);

AccountCreateController.$inject = ['$state', '$stateParams', 'Settings', 'Account', 'User', 'HLFields',
    'HLForms', 'HLUtils'];
function AccountCreateController($state, $stateParams, Settings, Account, User, HLFields, HLForms, HLUtils) {
    var vm = this;
    vm.account = {};
    vm.people = [];
    vm.tags = [];
    vm.errors = {
        name: [],
    };

    vm.loadDataproviderData = loadDataproviderData;
    vm.saveAccount = saveAccount;
    vm.cancelAccountCreation = cancelAccountCreation;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;
    vm.setStatusForCustomerId = setStatusForCustomerId;

    activate();

    ////

    function activate() {
        var choiceFields = ['status'];

        User.query().$promise.then(function(response) {
            angular.forEach(response.results, function(user) {
                if (user.first_name !== '') {
                    vm.people.push({
                        id: user.id,
                        // Convert to single string so searching with spaces becomes possible
                        name: HLUtils.getFullName(user),
                    });
                }
            });
        });

        Account.getFormOptions(function(data) {
            var choiceData = data.actions.POST;

            for (var i = 0; i < choiceFields.length; i++) {
                var splitName = choiceFields[i].split('_');
                var choiceVarName = splitName[0];

                // Convert to camelCase.
                if (splitName.length > 1) {
                    for (var j = 1; j < splitName.length; j++) {
                        choiceVarName += splitName[j].charAt(0).toUpperCase() + splitName[j].slice(1);
                    }
                }

                // Make the variable name a bit more logical (e.g. vm.stageChoices vs vm.stage).
                choiceVarName += 'Choices';

                vm[choiceVarName] = choiceData[choiceFields[i]].choices;
            }
        });

        _getAccount();
    }

    function _getAccount() {
        // Fetch the account or create empty account
        if ($stateParams.id) {
            Account.get({id: $stateParams.id}).$promise.then(function(account) {
                Settings.page.setAllTitles('edit', account.name);

                vm.account = account;

                angular.forEach(account.websites, function(website) {
                    if (website.is_primary) {
                        vm.account.primaryWebsite = website.website;
                    }
                });
                if (!vm.account.primaryWebsite || vm.account.primaryWebsite === '') {
                    vm.account.primaryWebsite = '';
                }

                if (vm.account.tags.length) {
                    var tags = [];
                    angular.forEach(account.tags, function(tag) {
                        tags.push(tag.name);
                    });
                    vm.account.tags = tags;
                }

                if (vm.account.assigned_to) {
                    vm.account.assigned_to = vm.account.assigned_to.id;
                }

                if (vm.account.hasOwnProperty('social_media') && vm.account.social_media.length) {
                    angular.forEach(vm.account.social_media, function(profile) {
                        vm.account[profile.name] = profile.username;
                    });
                }
            });
        } else {
            Settings.page.setAllTitles('create', 'account');

            vm.account = Account.create();

            User.me().$promise.then(function(user) {
                vm.account.assigned_to = user.id;
            });

            if (Settings.email.data && Settings.email.data.website) {
                vm.account.primaryWebsite = Settings.email.data.website;

                vm.account.getDataproviderInfo(Settings.email.data.website).then(function() {
                    if (!vm.account.name) {
                        var company = Settings.email.data.website.split('.').slice(0, -1).join(' ');
                        vm.account.name = company.charAt(0).toUpperCase() + company.slice(1);
                    }
                });
            }
        }
    }

    function loadDataproviderData(form) {
        toastr.info('Running around the world to fetch info', 'Here we go');
        vm.account.getDataproviderInfo(form.primaryWebsite.$modelValue).then(function() {
            toastr.success('Got it!', 'Whoohoo');
        }, function() {
            toastr.error('I couldn\'t find any data', 'Sorry');
        });
    }

    function addRelatedField(field) {
        HLFields.addRelatedField(vm.account, field);
    }

    function removeRelatedField(field, index, remove) {
        HLFields.removeRelatedField(vm.account, field, index, remove);
    }

    function cancelAccountCreation() {
        if (Settings.email.sidebar.form === 'account') {
            Settings.email.sidebar.form = null;
            Settings.email.sidebar.account = false;
        } else {
            $state.go('base.accounts');
        }
    }

    function saveAccount(form) {
        HLForms.blockUI();

        var primaryWebsite = vm.account.primaryWebsite;
        // Make sure it's not an empty website being added
        if (primaryWebsite && primaryWebsite !== 'http://' && primaryWebsite !== 'https://') {
            var exists = false;
            angular.forEach(vm.account.websites, function(website) {
                if (website.is_primary) {
                    website.website = primaryWebsite;
                    exists = true;
                }
            });

            if (!exists) {
                vm.account.websites.unshift({website: primaryWebsite, is_primary: true});
            }
        }

        // If the account is edited and the assigned to isn't changed, it's an object
        // So if that's the case get the id and set 'assigned_to' to that value
        if (typeof vm.account.assigned_to === 'object' && vm.account.assigned_to && vm.account.assigned_to.id) {
            vm.account.assigned_to = vm.account.assigned_to.id;
        }

        if (vm.account.tags && vm.account.tags.length) {
            var tags = [];
            angular.forEach(vm.account.tags, function(tag) {
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

        if (vm.account.twitter) {
            vm.account.social_media = [{
                name: 'twitter',
                username: vm.account.twitter,
            }];
        }

        vm.account = HLFields.cleanRelatedFields(vm.account, 'account');

        if (vm.account.id) {
            // If there's an ID set it means we're dealing with an existing account, so update it
            vm.account.$update(function() {
                toastr.success('I\'ve updated the account for you!', 'Done');
                $state.go('base.accounts.detail', {id: vm.account.id}, {reload: true});
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            vm.account.$save(function() {
                toastr.success('I\'ve saved the account for you!', 'Yay');

                if (Settings.email.sidebar.form === 'account') {
                    if (!Settings.email.data.contact.id) {
                        Settings.email.sidebar.form = 'contact';
                        Settings.email.data.account = vm.account;
                    } else {
                        Settings.email.sidebar.account = true;
                        Settings.email.sidebar.form = null;
                    }

                    Settings.email.data.account = vm.account;
                } else {
                    $state.go('base.accounts.detail', {id: vm.account.id});
                }
            }, function(response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function _handleBadResponse(response, form) {
        // Set error of the first website as the primary website error
        if (vm.account.primaryWebsite && response.data.websites && response.data.websites.length) {
            response.data.primaryWebsite = response.data.websites.shift()['website'];
        }

        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    function setStatusForCustomerId() {
        if (vm.account.status === '' || vm.account.status === 'inactive') {
            console.log('asdf');
            vm.account.status = 'active';
        }
    }
}
