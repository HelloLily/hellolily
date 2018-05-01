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
            currentContact: () => {
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
            currentContact: ['Contact', '$stateParams', (Contact, $stateParams) => {
                const contactId = $stateParams.id;
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
            currentContact: () => {
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
    let vm = this;

    vm.contact = currentContact || {};
    vm.errors = {
        name: [],
    };
    vm.accountSuggestions = {name: [], email: [], phone: []};
    vm.contactSuggestions = {name: [], email: [], phone: []};
    vm.showSuggestions = {name: true, email: true, phone: true};

    vm.saveContact = saveContact;
    vm.cancelContactCreation = cancelContactCreation;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;
    vm.refreshAccounts = refreshAccounts;
    vm.checkExistingContact = checkExistingContact;
    vm.contactForm = $stateParams.contactForm;
    vm.accountForm = $stateParams.accountForm;
    vm.mergeContactData = mergeContactData;
    vm.addAccount = addAccount;
    vm.searchEmailAddress = searchEmailAddress;
    vm.searchPhoneNumber = searchPhoneNumber;
    vm.addWorksAt = addWorksAt;

    activate();

    $scope.$watch('settings.email.sidebar.contactId', (newValue, oldValue) => {
        if (newValue) {
            Contact.get({id: newValue}).$promise.then(result => {
                vm.contact = _mergeData(result, Settings.email.sidebar.contactForm);
                activate();
            });
        }
    }, true);

    ////

    function activate() {
        _getContact();
        $timeout(() => {
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
                angular.forEach(vm.contact.social_media, profile => {
                    vm.contact[profile.name] = profile.username;
                });
            }
        } else {
            Settings.page.setAllTitles('create', 'contact');
            vm.contact = Contact.create();

            if ($stateParams.accountId) {
                Account.get({id: $stateParams.accountId}, account => {
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
        let result = secondary.filter(secondaryItem => {
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

        let twitterId;
        let linkedinId;

        if (vm.contact.hasOwnProperty('social_media')) {
            // Store the ids of the current social media objects.
            vm.contact.social_media.forEach(value => {
                if (value.name === 'twitter') {
                    twitterId = value.id;
                } else if (value.name === 'linkedin') {
                    linkedinId = value.id;
                }
            });
        }

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

        let copiedContact = angular.copy(vm.contact);
        let accounts = [];

        if (copiedContact.accounts && copiedContact.accounts.length) {
            copiedContact.accounts.forEach(account => {
                if (account) {
                    accounts.push({id: account.id});
                }
            });

            copiedContact.accounts = accounts;
        }

        if (copiedContact.id) {
            // If there's an ID set it means we're dealing with an existing contact, so update it
            copiedContact.$update(() => {
                toastr.success('I\'ve updated the contact for you!', 'Done');
                if (Settings.email.sidebar.form === 'contact') {
                    Settings.email.sidebar.form = null;
                    Settings.email.sidebar.contact = true;
                    Settings.email.data.contact = vm.contact;
                } else {
                    $state.go('base.contacts.detail', {id: copiedContact.id}, {reload: true});
                }
            }, response => {
                _handleBadResponse(response, form);
            });
        } else {
            copiedContact.$save(() => {
                toastr.success('I\'ve saved the contact for you!', 'Yay');

                _postSave(copiedContact);
            }, response => {
                _handleBadResponse(response, form);
            });
        }
    }

    function refreshAccounts(query) {
        if (!vm.accounts || query.length) {
            let accountsPromise = HLSearch.refreshList(query, 'Account');

            if (accountsPromise) {
                accountsPromise.$promise.then(data => {
                    vm.accounts = data.objects;
                });
            }
        }
    }

    function addAccount($select) {
        let account = Account.create();
        account.name = $select.search;
        account.status = Account.defaultNewStatus.id;
        account.assigned_to = currentUser.id;

        account.$save(response => {
            vm.contact.accounts.push(account);
            $select.close();
        });
    }

    function checkExistingContact() {
        if (!vm.contact.id && vm.contact.first_name && vm.contact.last_name) {
            const filterquery = `full_name:"${vm.contact.first_name} ${vm.contact.last_name}"`;

            Contact.search({filterquery}).$promise.then(results => {
                vm.contactSuggestions.name = results.objects;
                vm.showSuggestions.name = true;
            });
        }
    }

    function searchEmailAddress(emailAddress) {
        if (!vm.contact.id && emailAddress) {
            // There was a call for the current user, so try to find an account with the given email address.
            Account.searchByEmail({email_address: emailAddress}).$promise.then(response => {
                const {type} = response;

                if (type === 'account') {
                    const exists = vm.accountSuggestions.email.some(suggestion => suggestion.account.id === response.data.id);
                    const alreadyAdded = vm.contact.accounts.some(contactAccount => contactAccount.id === response.data.id);

                    if (!exists && !alreadyAdded) vm.accountSuggestions.email.push({emailAddress, account: response.data});

                    vm.showSuggestions.email = true;
                } else if (type === 'contact') {
                    const exists = vm.contactSuggestions.email.some(suggestion => suggestion.contact.id === response.data.id);

                    if (!exists) vm.contactSuggestions.email.push({emailAddress, contact: response.data});

                    vm.showSuggestions.email = true;
                }
            });
        }
    }

    function searchPhoneNumber(phoneNumber) {
        if (!vm.contact.id && phoneNumber) {
            // There was a call for the current user, so try to find an account or contact with the given number.
            Account.searchByPhoneNumber({number: phoneNumber}).$promise.then(response => {
                if (response.data.account) {
                    const account = response.data.account;
                    const exists = vm.accountSuggestions.phone.some(suggestion => suggestion.account.id === account.id);
                    const alreadyAdded = vm.contact.accounts.some(contactAccount => contactAccount.id === response.data.id);

                    if (!exists && !alreadyAdded) vm.accountSuggestions.phone.push({phoneNumber, account});

                    vm.showSuggestions.phone = true;
                } else if (response.data.contact) {
                    const contact = response.data.contact;
                    const exists = vm.contactSuggestions.phone.some(suggestion => suggestion.contact.id === contact.id);

                    if (!exists) vm.contactSuggestions.phone.push({phoneNumber, contact});

                    vm.showSuggestions.phone = true;
                }
            });
        }
    }

    function addWorksAt(account, type) {
        vm.contact.accounts.push(account);

        // Remove the added account from the suggestions.
        const index = vm.accountSuggestions[type].indexOf(account);
        vm.accountSuggestions[type].splice(index, 1);
    }

    function mergeContactData(contact) {
        Settings.email.sidebar.form = 'contact';
        Settings.email.sidebar.contactId = contact.id;
        Settings.email.sidebar.contactForm = vm.contact;

        // Clear the suggestions.
        for (let key in vm.contactSuggestions) {
            vm.contactSuggestions[key] = {};
        }
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

    $scope.$watch('vm.contact.accounts', () => {
        if (vm.contact.accounts) {
            if (vm.contact.accounts.length === 1) {
                Account.get({id: vm.contact.accounts[0].id}, account => {
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

    $scope.$on('saveContact', () => {
        saveContact($scope.contactForm);
    });
}
