/**
 * Router definition.
 */
angular.module('app.contacts').config(contactConfig);

contactConfig.$inject = ['$stateProvider'];
function contactConfig($stateProvider) {
    $stateProvider.state('base.contacts.create', {
        url: '/create',
        params: {
            'accountForm': null,
        },
        views: {
            '@': {
                templateUrl: 'contacts/controllers/form.html',
                controller: ContactCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
        resolve: {
            currentContact: function() {
                return null;
            },
        },
    });

    $stateProvider.state('base.contacts.detail.edit', {
        url: '/edit',
        params: {
            'accountForm': null,
            'contactForm': null,
        },
        views: {
            '@': {
                templateUrl: 'contacts/controllers/form.html',
                controller: ContactCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Edit',
        },
        resolve: {
            currentContact: ['Contact', '$stateParams', function(Contact, $stateParams) {
                var contactId = $stateParams.id;
                return Contact.get({id: contactId}).$promise;
            }],
        },
    });

    $stateProvider.state('base.contacts.create.fromAccount', {
        url: '/account/{accountId:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'contacts/controllers/form.html',
                controller: ContactCreateUpdateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            skip: true,
        },
        resolve: {
            currentContact: function() {
                return null;
            },
        },
    });
}

/**
 * Controller to create a new contact.
 */
angular.module('app.contacts').controller('ContactCreateUpdateController', ContactCreateUpdateController);

ContactCreateUpdateController.$inject = ['$scope', '$state', '$stateParams', '$timeout', 'Account',
    'Contact', 'HLFields', 'HLForms', 'HLResource', 'HLSearch', 'HLUtils', 'Settings', 'currentContact'];
function ContactCreateUpdateController($scope, $state, $stateParams, $timeout, Account, Contact,
    HLFields, HLForms, HLResource, HLSearch, HLUtils, Settings, currentContact) {
    var vm = this;

    vm.contact = currentContact || {};
    vm.errors = {
        name: [],
    };

    vm.saveContact = saveContact;
    vm.cancelContactCreation = cancelContactCreation;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;
    vm.refreshAccounts = refreshAccounts;
    vm.checkExistingContact = checkExistingContact;
    vm.contactForm = $stateParams.contactForm;
    vm.accountForm = $stateParams.accountForm;
    vm.mergeContactData = mergeContactData;

    activate();

    $scope.$watch('settings.email.sidebar.contactId', function(newValue, oldValue) {
        if (newValue) {
            Contact.get({id: newValue}).$promise.then(function(result) {
                vm.contact = _mergeData(result, Settings.email.sidebar.contactForm);
                activate();
            });
        }
    }, true);

    ////

    function activate() {
        vm.contactSuggestions = [];
        _getContact();
        $timeout(function() {
            // Focus the first input on page load.
            angular.element('.form-control')[0].focus();
            $scope.$apply();
        });
    }

    function _getContact() {
        // Fetch the contact or create empty contact.

        if (vm.contact.hasOwnProperty('id')) {
            Settings.page.setAllTitles('edit', vm.contact.full_name);

            if (vm.contactForm) {
                // Merge form data with current contact
                vm.contact = _mergeData(vm.contact, vm.contactForm);
            }

            if (vm.contact.hasOwnProperty('social_media') && vm.contact.social_media.length) {
                angular.forEach(vm.contact.social_media, function(profile) {
                    vm.contact[profile.name] = profile.username;
                });
            }
        } else {
            Settings.page.setAllTitles('create', 'contact');
            vm.contact = Contact.create();

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}, function(account) {
                    vm.contact.accounts.push(account);
                    vm.account = account;
                });
            }

            if ($stateParams.accountForm) {
                vm.contact.description = $stateParams.accountForm.description;
                vm.contact.email_addresses = $stateParams.accountForm.email_addresses;
                vm.contact.phone_numbers = $stateParams.accountForm.phone_numbers;
                vm.contact.addresses = $stateParams.accountForm.addresses;
            }

            if (Settings.email.data) {
                // Auto fill data if it's available
                if (Settings.email.data.contact) {
                    let contact = Settings.email.data.contact;

                    if (Settings.email.data.contact.firstName) {
                        vm.contact.first_name = Settings.email.data.contact.firstName;
                    }

                    if (Settings.email.data.contact.lastName) {
                        vm.contact.last_name = Settings.email.data.contact.lastName;
                    }

                    checkExistingContact();

                    if (Settings.email.data.contact.emailAddress) {
                        vm.contact.email_addresses.push({
                            email_address: Settings.email.data.contact.emailAddress,
                            status: 2,
                        });
                    }

                    if (contact.phoneNumbers) {
                        contact.phoneNumbers.$promise.then((data) => {
                            if (data.phone_numbers.length) {
                                // Phone number was added through the phoneNumbers directive.
                                // So clear it and add extracted phone number(s).
                                if (vm.contact.phone_numbers.length && !vm.contact.phone_numbers[0].hasOwnProperty('number')) {
                                    vm.contact.phone_numbers.shift();
                                }

                                data.phone_numbers.map((number) => {
                                    vm.contact.phone_numbers.push(HLUtils.formatPhoneNumber({type: 'work', number: number}));
                                });
                            }
                        });
                    }
                }

                if (Settings.email.data.account) {
                    vm.contact.accounts.push(Settings.email.data.account);
                }
            }
        }
    }

    function _mergeData(primary, dirtyForm) {
        const form = HLFields.cleanRelatedFields(dirtyForm);

        if (form.description) {
            primary.description = `${form.description}\n\n${primary.description}`;
        }

        // Don't add account if it already exists in the other contact
        primary.accounts = primary.accounts.concat(
            form.accounts.filter(account => {
                if (primary.accounts.find(x => x.id === account.id)) return false;
                return true;
            })
        );

        primary.email_addresses = _concatUnique(primary.email_addresses, form.email_addresses, ['email_address']);
        primary.phone_numbers = _concatUnique(primary.phone_numbers, form.phone_numbers, ['number']);
        primary.addresses = _concatUnique(primary.addresses, form.addresses, ['address', 'city', 'postal_code']);
        if (!primary.twitter && form.twitter) primary.twitter = form.twitter;
        if (!primary.linkedin && form.linkedin) primary.linkedin = form.linkedin;
        primary.tags = _concatUnique(primary.tags, form.tags, ['name']);
        return primary;
    }

    function _concatUnique(primary, secondary, unique) {
        // Remove items already present in primary from secondary.
        let result = secondary.filter(function(secondaryItem) {
            // Check if all unique keys are the same, remove item from array if they are.
            let count = 0;

            unique.map(key => {
                if (primary.find(primaryItem => primaryItem[key] === secondaryItem[key])) {
                    count++;
                }
            });

            return count !== unique.length;
        });

        return primary.concat(result);
    }

    function addRelatedField(field) {
        HLFields.addRelatedField(vm.contact, field);
    }

    function removeRelatedField(field, index, remove) {
        HLFields.removeRelatedField(vm.contact, field, index, remove);
    }

    function cancelContactCreation() {
        if (Settings.email.sidebar.form === 'contact') {
            Settings.email.sidebar.form = null;
            Settings.email.sidebar.contact = false;
        } else {
            if (Settings.page.previousState && !Settings.page.previousState.state.abstract) {
                // Check if we're coming from another page.
                $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
            } else {
                $state.go('base.contacts');
            }
        }
    }

    function saveContact(form) {
        var accounts = [];
        var copiedContact;
        var twitterId;
        var linkedinId;

        // Check if a contact is being added via the + contact page or via
        // a supercard.
        if (Settings.email.sidebar.isVisible) {
            ga('send', 'event', 'Contact', 'Save', 'Email Sidebar');
        } else {
            if ($stateParams.accountId) {
                ga('send', 'event', 'Contact', 'Save', 'Account Widget');
            } else {
                ga('send', 'event', 'Contact', 'Save', 'Default');
            }
        }

        HLForms.blockUI();
        HLForms.clearErrors(form);

        // Store the ids of the current social media objects.
        angular.forEach(vm.contact.social_media, function(value) {
            if (value.name === 'twitter') {
                twitterId = value.id;
            } else if (value.name === 'linkedin') {
                linkedinId = value.id;
            }
        });

        vm.contact.social_media = [];
        if (vm.contact.twitter) {
            vm.contact.social_media.push({
                name: 'twitter',
                username: vm.contact.twitter,
            });
            // Re-use social media id in case of an edit.
            if (twitterId) {
                vm.contact.social_media[vm.contact.social_media.length - 1].id = twitterId;
            }
        }

        if (vm.contact.linkedin) {
            vm.contact.social_media.push({
                name: 'linkedin',
                username: vm.contact.linkedin,
            });
            // Re-use social media ids in case of an edit.
            if (linkedinId) {
                vm.contact.social_media[vm.contact.social_media.length - 1].id = linkedinId;
            }
        }

        vm.contact = HLFields.cleanRelatedFields(vm.contact);

        copiedContact = angular.copy(vm.contact);

        if (copiedContact.accounts && copiedContact.accounts.length) {
            angular.forEach(copiedContact.accounts, function(account) {
                if (account) {
                    accounts.push({id: account.id});
                }
            });

            copiedContact.accounts = accounts;
        }

        if (copiedContact.id) {
            // If there's an ID set it means we're dealing with an existing contact, so update it
            copiedContact.$update(function() {
                toastr.success('I\'ve updated the contact for you!', 'Done');
                if (Settings.email.sidebar.form === 'contact') {
                    Settings.email.sidebar.form = null;
                    Settings.email.sidebar.contact = true;
                    Settings.email.data.contact = vm.contact;
                } else {
                    $state.go('base.contacts.detail', {id: copiedContact.id}, {reload: true});
                }
            }, function(response) {
                _handleBadResponse(response, form);
            });
        } else {
            copiedContact.$save(function() {
                toastr.success('I\'ve saved the contact for you!', 'Yay');

                _postSave(copiedContact);
            }, function(response) {
                _handleBadResponse(response, form);
            });
        }
    }

    function refreshAccounts(query) {
        var accountsPromise;

        if (!vm.accounts || query.length) {
            accountsPromise = HLSearch.refreshList(query, 'Account');

            if (accountsPromise) {
                accountsPromise.$promise.then(function(data) {
                    vm.accounts = data.objects;
                });
            }
        }
    }

    function checkExistingContact() {
        var fullName;

        if (!vm.contact.id && vm.contact.first_name && vm.contact.last_name) {
            fullName = vm.contact.first_name + ' ' + vm.contact.last_name;

            Contact.search({filterquery: 'full_name:"' + fullName + '"'}).$promise.then(function(results) {
                vm.contactSuggestions = results.objects;
            });
        }
    }

    function mergeContactData(contactId) {
        Settings.email.sidebar.form = 'contact';
        Settings.email.sidebar.contactId = contactId;
        Settings.email.sidebar.contactForm = vm.contact;
    }

    function _postSave(contact) {
        new Intercom('trackEvent', 'contact-created');
        if (Settings.email.sidebar.form === 'contact') {
            Settings.email.sidebar.form = null;
            Settings.email.sidebar.contact = true;
            Settings.email.data.contact = contact;
        } else {
            if ($stateParams.accountId) {
                // Redirect back to account if contact was created from the account page.
                $state.go('base.accounts.detail', {id: $stateParams.accountId}, {reload: true});
            } else {
                $state.go('base.contacts.detail', {id: contact.id}, {reload: true});
            }
        }
    }

    $scope.$watch('vm.contact.accounts', function() {
        if (vm.contact.accounts) {
            if (vm.contact.accounts.length === 1) {
                Account.get({id: vm.contact.accounts[0].id}, function(account) {
                    if (!vm.account || vm.account.id !== account.id) {
                        vm.account = account;
                    }
                });
            } else if (vm.contact.accounts.length === 0) {
                vm.account = null;
            }
        }
    }, true);

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        // Recreate empty related fields
        if (!vm.contact.email_addresses.length) vm.addRelatedField('emailAddress');
        if (!vm.contact.phone_numbers.length) vm.addRelatedField('phoneNumber');
        if (!vm.contact.addresses.length) vm.addRelatedField('address');

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    $scope.$on('saveContact', function() {
        saveContact($scope.contactForm);
    });
}
