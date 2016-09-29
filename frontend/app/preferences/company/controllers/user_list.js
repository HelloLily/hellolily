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
            label: 'Users',
        },
        resolve: {
            userList: ['User', function(User) {
                return User.query().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesCompanyUserList', PreferencesCompanyUserList);

PreferencesCompanyUserList.$inject = ['$compile', '$scope', '$templateCache', 'LocalStorage', 'Settings',
    'User', 'UserTeams'];
function PreferencesCompanyUserList($compile, $scope, $templateCache, LocalStorage, Settings, User, UserTeams) {
    var vm = this;
    var storage = new LocalStorage('userList');

    Settings.page.setAllTitles('list', 'users');

    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        order: storage.get('order', {
            descending: false,
            column: 'full_name',  // string: current sorted column
        }),
        statusFilter: storage.get('statusFilter', 'True'),
        statusFilterOpen: false,
        visibility: storage.get('visibility', {
            full_name: true,
            email: true,
            phone_number: true,
            is_active: true,
        }),
    };
    vm.alertMessages = messages.alerts.deactivateUser;

    vm.openTeamModal = openTeamModal;
    vm.toggleStatus = toggleStatus;

    activate();

    /////////////

    function activate() {
        UserTeams.query().$promise.then(function(response) {
            vm.teamList = response.results;
        });

        _setupWatches();
    }

    function _setupWatches() {
        /**
         * Watches the model info from the status filter that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watch('vm.table.statusFilter', function() {
            _updateStatusFilter();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup(['vm.table.page', 'vm.table.order.column', 'vm.table.order.descending'], function() {
            _updateTableSettings();
            _updateUsers();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
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
    }

    function _updateUsers() {
        var column;
        var ordering;
        if (vm.table.order.column === 'full_name') {
            // Special case for full_name, since it's not a db field we can't really order by it.
            if (vm.table.order.descending) {
                column = 'first_name,-preposition,-last_name';
            } else {
                column = 'first_name,preposition,last_name';
            }
        } else {
            column = vm.table.order.column;
        }
        ordering = ((vm.table.order.descending) ? '-' + column : column);

        User.query({
            'is_active': vm.table.statusFilter,
            'page': vm.table.page,
            'page_size': vm.table.pageSize,
            'ordering': ordering,
        }, function(response) {
            vm.table.items = response.results;
            vm.table.totalItems = response.pagination.total;
        }, function() {
            vm.table.items = [];
            vm.table.totalItems = 0;

            toastr.error('Could not load the user list, please try again later.', 'Error');
        });
    }

    function openTeamModal(user) {
        vm.user = user;

        vm.teamList.forEach(function(team) {
            var selected = vm.user.teams.filter(function(teamId) {
                return teamId === team.id;
            });

            team.selected = selected.length > 0;
        });

        swal({
            title: sprintf(messages.alerts.preferences.userAssignTitle, {user: user.full_name}),
            html: $compile($templateCache.get('preferences/company/controllers/user_teams_modal.html'))($scope),
            showCancelButton: true,
            showCloseButton: true,
        }).then(function(isConfirm) {
            var selectedTeams = [];
            var args = {
                id: user.id,
            };

            if (isConfirm) {
                // Loop over emailAccountList to extract the selected accounts.
                vm.teamList.forEach(function(team) {
                    if (team.selected) {
                        selectedTeams.push(team.id);
                    }
                });

                args.teams = selectedTeams;

                User.patch(args).$promise.then(function() {
                    toastr.success('I\'ve updated the users\' teams for you!', 'Done');
                }, function(response) {
                    HLForms.setErrors(form, response.data);
                    toastr.error('Uh oh, there seems to be a problem', 'Oops!');
                });
            }
        }).done();
    }

    function toggleStatus(user) {
        var index;

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
            user.is_active = !user.is_active;

            User.patch({
                id: user.id,
                is_active: 'All',
            }, {
                'is_active': 'true',  // Make the user active.
            }, function() {
                toastr.success('I\'ve activated the user for you!', 'Done');
            }, function() {
                toastr.error('Uh oh, there seems to be a problem', 'Oops!');
            });

            if (vm.table.statusFilter === 'False') {
                // If we display only inactive statusses, remove the newly activated user from the list.
                index = vm.table.items.indexOf(user);
                vm.table.items.splice(index, 1);
            }
        }
    }
}
