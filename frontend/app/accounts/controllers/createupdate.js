
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts.create', {
        url: '/create?name&phone_number',
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
        resolve: {
            currentAccount: () => {
                return null;
            },
        },
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        params: {
            'accountForm': null,
        },
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
        resolve: {
            currentAccount: ['Account', '$stateParams', (Account, $stateParams) => {
                return Account.get({id: $stateParams.id}).$promise;
            }],
        },
    });
}

/**
 * Controller to create a new account.
 */
angular.module('app.accounts').controller('AccountCreateController', AccountCreateController);

AccountCreateController.$inject = ['$scope', '$state', '$stateParams', '$timeout', 'Account', 'HLFields', 'HLForms',
    'HLSearch', 'HLUtils', 'Settings', 'User', 'currentAccount'];
function AccountCreateController($scope, $state, $stateParams, $timeout, Account, HLFields, HLForms,
    HLSearch, HLUtils, Settings, User, currentAccount) {
    const vm = this;

    vm.account = currentAccount || {};
    vm.accountSuggestions = {name: [], email: [], phone: []};
    vm.contactSuggestions = {name: [], email: [], phone: []};
    vm.showSuggestions = {name: true, email: true, phone: true};
    vm.tags = [];
    vm.errors = {
        name: [],
    };
    vm.useDuplicateWebsite = false;

    vm.loadDataproviderData = loadDataproviderData;
    vm.saveAccount = saveAccount;
    vm.cancelAccountCreation = cancelAccountCreation;
    vm.addRelatedField = addRelatedField;
    vm.removeRelatedField = removeRelatedField;
    vm.setStatusForCustomerId = setStatusForCustomerId;
    vm.checkExistingAccount = checkExistingAccount;
    vm.refreshUsers = refreshUsers;
    vm.assignToMe = assignToMe;
    vm.callerNumber = $stateParams.phone_number;
    vm.accountForm = $stateParams.accountForm;
    vm.mergeAccountData = mergeAccountData;
    vm.searchEmailAddress = searchEmailAddress;
    vm.searchPhoneNumber = searchPhoneNumber;

    activate();

    $scope.$watch('settings.email.sidebar.accountId', (newValue, oldValue) => {
        if (newValue) {
            Account.get({id: newValue}).$promise.then(result => {
                vm.account = _mergeData(result, Settings.email.sidebar.accountForm);
                activate();
            });
        }
    }, true);

    ////

    function activate() {
        User.me().$promise.then(user => {
            vm.currentUser = user;

            Account.getStatuses(response => {
                vm.statusChoices = response.results;
                vm.defaultNewStatus = Account.defaultNewStatus;
                vm.relationStatus = Account.relationStatus;
                vm.activeStatus = Account.activeStatus;

                // Getting the statusses includes which status is the default for a new account,
                // so get (or create) the account afterwards.
                _getAccount();
            });
        });

        $timeout(() => {
            // Focus the first input on page load.
            angular.element('input')[0].focus();
            $scope.$apply();
        });
    }

    function _getAccount() {
        // Fetch the account or create empty account
        if (vm.account.hasOwnProperty('id')) {
            Settings.page.setAllTitles('edit', vm.account.name);

            if (vm.accountForm) {
                // Merge form data with current account
                vm.account = _mergeData(vm.account, vm.accountForm);
            }

            vm.account.websites.forEach(website => {
                if (website.is_primary) {
                    vm.account.primary_website = website.website;
                }
            });
            if (!vm.account.primary_website || vm.account.primary_website === '') {
                vm.account.primary_website = '';
            }

            if (vm.account.hasOwnProperty('social_media') && vm.account.social_media.length) {
                vm.account.social_media.forEach(profile => {
                    vm.account[profile.name] = profile.username;
                });
            }
        } else {
            Settings.page.setAllTitles('create', 'account');

            vm.account = Account.create();
            vm.account.status = vm.defaultNewStatus;
            vm.account.name = $stateParams.name;
            vm.account.assigned_to = vm.currentUser;

            if (vm.callerNumber) {
                vm.account.phone_numbers.push({
                    'number': $stateParams.phone_number,
                    'type': 'work',
                });

                vm.account.getDataproviderInfoByPhoneNumber(vm.callerNumber).then(() => {
                    // With the retrieved info it is possible that the account already exists.
                    vm.checkExistingAccount();
                });
            }

            if (Settings.email.data && Settings.email.data.website) {
                vm.account.primary_website = Settings.email.data.website;

                vm.account.getDataproviderInfoByUrl(Settings.email.data.website).then(() => {
                    if (!vm.account.name) {
                        const company = Settings.email.data.website.split('.').slice(0, -1).join(' ');
                        vm.account.name = company.charAt(0).toUpperCase() + company.slice(1);
                    }
                });
            }
        }
    }

    function _mergeData(primary, dirtyForm) {
        const form = HLFields.cleanRelatedFields(dirtyForm);

        if (!primary.primary_website) primary.primary_website = form.primary_website;
        if (form.description) {
            primary.description = `${form.description}\n\n${primary.description}`;
        }
        primary.email_addresses = _concatUnique(primary.email_addresses, form.email_addresses, ['email_address']);
        primary.phone_numbers = _concatUnique(primary.phone_numbers, form.phone_numbers, ['number']);
        primary.addresses = _concatUnique(primary.addresses, form.addresses, ['address', 'city', 'postal_code']);
        primary.websites = _concatUnique(primary.websites, form.websites, ['website']);
        if (!primary.twitter && form.twitter) primary.twitter = form.twitter;
        primary.tags = _concatUnique(primary.tags, form.tags, ['name']);
        return primary;
    }

    function _concatUnique(primary, secondary, unique) {
        // Remove items already present in primary from secondary.
        const result = secondary.filter(secondaryItem => {
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

    function checkExistingAccount() {
        if (!vm.account.id) {
            const filterquery = `domain:"${vm.account.primary_website}" OR name:"${vm.account.name}"`;

            Account.search({filterquery}).$promise.then(results => {
                vm.accountSuggestions.name = results.objects;
                vm.showSuggestions.name = true;
            });
        }
    }

    function searchEmailAddress(emailAddress) {
        if (!vm.account.id && emailAddress) {
            // There was a call for the current user, so try to find an account with the given email address.
            Account.searchByEmail({email_address: emailAddress}).$promise.then(response => {
                const {type} = response;

                if (type === 'account') {
                    const exists = vm.accountSuggestions.email.some(suggestion => suggestion.account.id === response.data.id);
                    if (!exists) vm.accountSuggestions.email.push({emailAddress, account: response.data});

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
        if (!vm.account.id && phoneNumber) {
            // There was a call for the current user, so try to find an account or contact with the given number.
            Account.searchByPhoneNumber({number: phoneNumber}).$promise.then(response => {
                if (response.data.account) {
                    const account = response.data.account;
                    const exists = vm.accountSuggestions.phone.some(suggestion => suggestion.account.id === account.id);

                    if (!exists) vm.accountSuggestions.phone.push({phoneNumber, account});

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

    function loadDataproviderData() {
        // Clear accountSuggestions because the assumption is that the user has tried with a new account.
        vm.accountSuggestions.name = [];

        toastr.info('Running around the world to fetch info', 'Here we go');
        vm.account.getDataproviderInfoByUrl(vm.account.primary_website).then(() => {
            toastr.success('Got it!', 'Whoohoo');
        }, () => {
            toastr.error('I couldn\'t find any data', 'Sorry');
        });

        // Rerun checkExistingAccount to notify the user that he is still using an existing domain.
        vm.checkExistingAccount();
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
            if (Settings.page.previousState && !Settings.page.previousState.state.abstract) {
                // Check if we're coming from another page.
                $state.go(Settings.page.previousState.state, Settings.page.previousState.params);
            } else {
                $state.go('base.accounts');
            }
        }
    }

    function mergeAccountData(account) {
        Settings.email.sidebar.form = 'account';
        Settings.email.sidebar.accountId = account.id;
        Settings.email.sidebar.accountForm = vm.account;

        // Clear the suggestions.
        for (let key in vm.accountSuggestions) {
            vm.accountSuggestions[key] = {};
        }
    }

    function saveAccount(form) {
        // Check if an account is being added via the + account page or via a supercard.
        if (Settings.email.sidebar.isVisible) {
            ga('send', 'event', 'Account', 'Save', 'Email Sidebar');
        } else {
            ga('send', 'event', 'Account', 'Save', 'Default');
        }

        HLForms.blockUI();

        const primaryWebsite = vm.account.primary_website;

        // Make sure it's not an empty website being added.
        if (primaryWebsite && primaryWebsite !== 'http://' && primaryWebsite !== 'https://') {
            let exists = false;

            angular.forEach(vm.account.websites, website => {
                if (website.is_primary) {
                    website.website = primaryWebsite;
                    exists = true;
                }
            });

            if (!exists) {
                vm.account.websites.unshift({website: primaryWebsite, is_primary: true});
            }
        }

        // If the account is edited and the 'assigned_to' isn't changed, it's an object.
        // So if that's the case get the id and set 'assigned_to' to that value.
        if (typeof vm.account.assigned_to === 'object' && vm.account.assigned_to && vm.account.assigned_to.id) {
            vm.account.assigned_to = vm.account.assigned_to.id;
        }

        // Rewrite submit so that it isn't sending the whole status object, but only its id.
        if (typeof vm.account.status === 'object' && vm.account.status && vm.account.status.id) {
            vm.account.status = {id: vm.account.status.id};
        }

        HLForms.clearErrors(form);

        let twitterId;

        // Store the id of the current twitter object.
        if (vm.account.social_media && vm.account.social_media.length > 0) {
            twitterId = vm.account.social_media[0].id;
        }

        if (vm.account.twitter) {
            vm.account.social_media = [{
                name: 'twitter',
                username: vm.account.twitter,
            }];
            // Re-use Twitter ID in case of an edit.
            if (twitterId) {
                vm.account.social_media[vm.account.social_media.length - 1].id = twitterId;
            }
        }

        vm.account = HLFields.cleanRelatedFields(vm.account);

        if (vm.account.id) {
            // If there's an ID set it means we're dealing with an existing account, so update it.
            vm.account.$update(() => {
                toastr.success('I\'ve updated the account for you!', 'Done');
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
                    $state.go('base.accounts.detail', {id: vm.account.id}, {reload: true});
                }
            }, response => {
                _handleBadResponse(response, form);
            });
        } else {
            vm.account.$save(() => {
                new Intercom('trackEvent', 'account-created');

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
            }, response => {
                _handleBadResponse(response, form);
            });
        }
    }

    function assignToMe() {
        vm.account.assigned_to = vm.currentUser;
    }

    function refreshUsers(query) {
        if (!vm.assigned_to || query.length) {
            const usersPromise = HLSearch.refreshList(query, 'User', 'is_active:true', 'full_name', 'full_name');

            if (usersPromise) {
                usersPromise.$promise.then(data => {
                    vm.users = data.objects;
                });
            }
        }
    }

    function _handleBadResponse(response, form) {
        // Set error of the first website as the primary website error.
        if (vm.account.primary_website && response.data.websites && response.data.websites.length) {
            response.data.primary_website = response.data.websites.shift().website;
        }

        HLForms.setErrors(form, response.data);

        // Recreate empty related fields
        if (!vm.account.email_addresses.length) vm.addRelatedField('emailAddress');
        if (!vm.account.phone_numbers.length) vm.addRelatedField('phoneNumber');
        if (!vm.account.addresses.length) vm.addRelatedField('address');
        if (!vm.account.websites.filter(website => website.is_primary === false).length) {
            vm.addRelatedField('website');
        }

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }

    function setStatusForCustomerId() {
        if (vm.account.status.id === vm.relationStatus.id) {
            vm.account.status = vm.activeStatus;
        }
    }

    $scope.$on('saveAccount', () => {
        saveAccount($scope.accountForm);
    });
}
