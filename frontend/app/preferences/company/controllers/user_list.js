angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.company.users', {
        url: '/users',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/company/controllers/user_list.html',
                controller: PreferencesCompanyUserList,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Accounts',
        },
        resolve: {
            invites: ['UserInvite', UserInvite => UserInvite.query({}).$promise],
        },
    });
}

angular.module('app.preferences').controller('PreferencesCompanyUserList', PreferencesCompanyUserList);

PreferencesCompanyUserList.$inject = ['$compile', '$scope', '$state', '$templateCache', 'HLForms', 'HLResource',
    'LocalStorage', 'Settings', 'User', 'UserInvite', 'UserTeams', 'invites'];
function PreferencesCompanyUserList($compile, $scope, $state, $templateCache, HLForms, HLResource,
    LocalStorage, Settings, User, UserInvite, UserTeams, invites) {
    const vm = this;
    const storage = new LocalStorage('userList');

    Settings.page.setAllTitles('list', 'users');

    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        order: storage.get('order', {
            descending: false,
            column: 'full_name',  // string: current sorted column
        }),
        statusFilter: storage.get('statusFilter', 1),
        statusFilterOpen: false,
        visibility: storage.get('visibility', {
            full_name: true,
            teams: true,
            email: true,
            phone_number: true,
            internal_number: true,
            is_active: true,
        }),
        searchQuery: storage.get('searchQuery', ''),
    };
    vm.alertMessages = messages.alerts.deactivateUser;
    vm.removeInviteMessages = messages.alerts.removeUserInvite;
    vm.invites = invites.results;
    vm.newTeam = UserTeams.create();

    vm.openTeamModal = openTeamModal;
    vm.toggleStatus = toggleStatus;
    vm.resendInvite = resendInvite;
    vm.removeInvite = removeInvite;
    vm.setSearchQuery = setSearchQuery;
    vm.addTeam = addTeam;
    vm.updateTeam = updateTeam;
    vm.updateModel = updateModel;

    activate();

    /////////////

    function activate() {
        _setupWatches();
    }

    function _setupWatches() {
        /**
         * Watches the model info from the status filter that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watch('vm.table.statusFilter', () => {
            _updateStatusFilter();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.descending',
            'vm.table.searchQuery',
        ], () => {
            _updateTableSettings();
            _updateUsers();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', () => {
            _updateTableSettings();
        });
    }

    function _updateStatusFilter() {
        // Close the status filter after clicking.
        vm.table.statusFilterOpen = false;

        storage.put('statusFilter', vm.table.statusFilter);

        _updateUsers();
    }

    function _updateTableSettings() {
        storage.put('order', vm.table.order);
        storage.put('visibility', vm.table.visibility);
        storage.put('searchQuery', vm.table.searchQuery);
    }

    function updateModel(data, field, userObject) {
        const internalNumber = parseInt(data);
        const foundUsers = vm.table.items.filter(user => user.internal_number === internalNumber);

        User.patch({
            id: userObject.id,
            is_active: 'All',
        }, {
            internal_number: internalNumber || null,
        }).$promise.then(() => {
            if (foundUsers.length > 0) {
                toastr.success(`The internal number for ${foundUsers[0].full_name} has been cleared`);
            }

            toastr.success(`The internal number for ${userObject.full_name} has been updated`, 'Done');

            _updateUsers();
        });
    }

    function _updateUsers() {
        if (vm.table.statusFilter !== 2) {
            const ordering = vm.table.order.descending ? '-' + vm.table.order.column : vm.table.order.column;
            const filterQuery = vm.table.statusFilter !== undefined ? `is_active:${vm.table.statusFilter}` : '';

            User.search({
                'filterquery': filterQuery,
                'page': vm.table.page - 1,
                'size': vm.table.pageSize,
                'sort': ordering,
                'q': vm.table.searchQuery,
            }, response => {
                vm.table.items = response.objects;
                vm.table.totalItems = response.total;

                if (filterQuery === '') {
                    // 'All' filter selected, so count invites as well.
                    vm.table.totalItems += vm.invites.length;
                }
            }, () => {
                vm.table.items = [];
                vm.table.totalItems = 0;

                toastr.error('Could not load the user list, please try again later.', 'Error');
            });
        } else {
            vm.table.items = [];
            vm.table.totalItems = vm.invites.length;
        }
    }

    function openTeamModal(user) {
        UserTeams.query().$promise.then(teamResponse => {
            vm.teamList = teamResponse.results;
            vm.user = user;

            // Loop through the list of teams to check if a user is in a team
            // and set the team to selected.
            vm.teamList.forEach(team => {
                team.users.forEach(teamUser => {
                    if (teamUser.id === vm.user.id) {
                        team.selected = true;
                    }
                });
            });

            swal({
                title: sprintf(messages.alerts.preferences.userAssignTitle, {user: user.full_name}),
                html: $compile($templateCache.get('preferences/company/controllers/user_teams_modal.html'))($scope),
                showCancelButton: true,
                showCloseButton: true,
            }).then(isConfirm => {
                const form = '[name="userTeamForm"]';
                const selectedTeams = [];
                const args = {
                    id: user.id,
                };

                if (isConfirm) {
                    // Loop over teamList to extract the selected accounts.
                    vm.teamList.forEach(team => {
                        selectedTeams.push({id: team.id, is_deleted: !team.selected});
                    });

                    args.teams = selectedTeams;

                    User.patch(args).$promise.then(() => {
                        toastr.success('I\'ve updated the users\' teams for you!', 'Done');
                        _updateUsers();
                    }, response => {
                        HLForms.setErrors(form, response.data);
                        toastr.error('Uh oh, there seems to be a problem', 'Oops');
                    });
                }
            }).done();
        });
    }

    function toggleStatus(user) {
        let index;

        if (user.is_active) {
            user.is_active = !user.is_active;

            // This is a callback from deleteConfirmation, that already does the api request to deactivate.
            if (vm.table.statusFilter === 'True') {
                // If we display only active statusses, remove the newly deactivated user from the list.
                index = vm.table.items.indexOf(user);
                vm.table.items.splice(index, 1);
            }

            $scope.$apply();  // Because this is a callback, explicitly call apply on the scope.
        } else {
            User.patch({
                id: user.id,
                is_active: 'All',
            }, {
                'is_active': 'true',  // Make the user active.
            }, () => {
                user.is_active = !user.is_active;
                toastr.success('I\'ve activated the user for you!', 'Done');
            }, () => {
                toastr.error('Uh oh, there seems to be a problem', 'Oops!');
            });

            if (vm.table.statusFilter === 'False') {
                // If we display only inactive statusses, remove the newly activated user from the list.
                index = vm.table.items.indexOf(user);
                vm.table.items.splice(index, 1);
            }
        }
    }

    function resendInvite(invite) {
        swal({
            title: messages.alerts.resendUserInvite.title,
            html: sprintf(messages.alerts.resendUserInvite.confirmText, {email: invite.email}),
            confirmButtonText: messages.alerts.resendUserInvite.confirmButtonText,
            showCancelButton: true,
            showCloseButton: true,
        }).then(isConfirm => {
            if (isConfirm) {
                UserInvite.post({invites: [invite]}).$promise.then(() => {
                    toastr.success(messages.alerts.resendUserInvite.success, 'Done');
                    $state.reload();
                });
            }
        }).done();
    }

    function addTeam() {
        vm.newTeam.$save(response => {
            toastr.success('Team has been saved', 'Done');

            vm.newTeam = UserTeams.create();
        }, error => {
            toastr.error('A team with that name already exists', 'Oops');
        });
    }

    function updateTeam(data, team) {
        const field = 'name';

        return UserTeams.updateModel(data, field, team);
    }

    function removeInvite() {
        $state.reload();
    }

    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }
}
