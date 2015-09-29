/**
 * Router definition.
 */
angular.module('app.contacts').config(contactConfig);

contactConfig.$inject = ['$stateProvider'];
function contactConfig($stateProvider) {
    $stateProvider.state('base.contacts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/form_outer.html',
                controller: ContactCreateUpdateController,
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

    $stateProvider.state('base.contacts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/form_outer.html',
                controller: ContactCreateUpdateController,
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
 * Controller to create a new contact.
 */
angular.module('app.contacts').controller('ContactCreateUpdateController', ContactCreateUpdateController);

ContactCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', 'Account', 'Contact', 'HLFields', 'HLForms', 'user'];
function ContactCreateUpdateController($scope, $state, $stateParams, Account, Contact, HLFields, HLForms, user) {
    var vm = this;
    vm.contact = {};
    vm.tags = [];
    vm.errors = {
        name: []
    };
    vm.accounts = [];

    vm.saveContact = saveContact;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;
    vm.currentUser = user;
    vm.refreshAccounts = refreshAccounts;

    activate();

    ////

    function activate() {
        $scope.conf.pageTitleSmall = 'change is natural';

        _getContact();
    }

    function _getContact() {
        // Fetch the contact or create empty contact
        if ($stateParams.id) {
            $scope.conf.pageTitleBig = 'Edit contact';
            Contact.get({id: $stateParams.id}).$promise.then(function (contact) {
                vm.contact = contact;

                if (vm.contact.hasOwnProperty('tags') && vm.contact.tags.length) {
                    var tags = [];
                    angular.forEach(vm.contact.tags, function (tag) {
                        tags.push(tag.name);
                    });

                    vm.contact.tags = tags;
                }

                if (vm.contact.hasOwnProperty('social_media') && vm.contact.social_media.length) {
                    angular.forEach(vm.contact.social_media, function (profile) {
                        vm.contact[profile.name] = profile.username;
                    });
                }

                $scope.conf.pageTitleBig = vm.contact.name;
            });
        } else {
            $scope.conf.pageTitleBig = 'New contact';
            vm.contact = Contact.create();
        }
    }

    function addRelatedField(field) {
        HLFields.addRelatedField(vm.contact, field);
    }

    function removeRelatedField(field, index, remove) {
        HLFields.removeRelatedField(vm.contact, field, index, remove);
    }

    function saveContact(form) {
        if (vm.contact.tags && vm.contact.tags.length) {
            var tags = [];

            angular.forEach(vm.contact.tags, function (tag) {
                if (tag) {
                    tags.push({name: (tag.name) ? tag.name : tag});
                }
            });

            vm.contact.tags = tags;
        }

        if (vm.contact.accounts && vm.contact.accounts.length) {
            var accounts = [];

            angular.forEach(vm.contact.accounts, function (account) {
                if (account) {
                    accounts.push({id: account.id});
                }
            });
        }

        // Clear all errors of the form (in case of new errors)
        angular.forEach(form, function(value, key) {
            if (typeof value === 'object' && value.hasOwnProperty('$modelValue')) {
                form[key].$error = {};
                form[key].$setValidity(key, true);
            }
        });

        vm.contact.social_media = [];

        if (vm.contact.twitter) {
            vm.contact.social_media.push({
                name: 'twitter',
                username: vm.contact.twitter
            })
        }

        if (vm.contact.linkedin) {
            vm.contact.social_media.push({
                name: 'linkedin',
                username: vm.contact.linkedin
            })
        }

        vm.contact = HLFields.cleanRelatedFields(vm.contact);

        if (vm.contact.id) {
            // If there's an ID set it means we're dealing with an existing contact, so update it
            vm.contact.$update(function () {
                toastr.success('I\'ve updated the contact for you!', 'Done');
                $state.go('base.contacts.detail', {id: vm.contact.id}, {reload: true});
            }, function (response) {
                _handleBadResponse(response, form);
            })
        }
        else {
            vm.contact.$save(function () {
                toastr.success('I\'ve saved the contact for you!', 'Yay');
                $state.go('base.contacts.detail', {id: vm.contact.id});
            }, function (response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function refreshAccounts(query) {
        if (query.length > 1) {
            vm.accounts = Account.search({filterquery: "name:(" + query + ")", size: 60});
        }
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }
}
