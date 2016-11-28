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
    });
}

angular.module('app.preferences').controller('PreferencesCompanyUserList', PreferencesCompanyUserList);

PreferencesCompanyUserList.$inject = ['$compile', '$scope', '$templateCache', 'HLForms', 'LocalStorage', 'Settings',
    'User', 'UserTeams'];
function PreferencesCompanyUserList($compile, $scope, $templateCache, HLForms, LocalStorage, Settings, User, UserTeams) {
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
        statusFilter: storage.get('statusFilter', 1),
        statusFilterOpen: false,
        visibility: storage.get('visibility', {
            full_name: true,
            email: true,
            phone_number: true,
            internal_number: true,
            is_active: true,
        }),
        searchQuery: storage.get('searchQuery', ''),
    };
    vm.alertMessages = messages.alerts.deactivateUser;

    vm.openTeamModal = openTeamModal;
    vm.toggleStatus = toggleStatus;
    vm.setSearchQuery = setSearchQuery;

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
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.descending',
            'vm.table.searchQuery',
        ], function() {
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
        storage.put('searchQuery', vm.table.searchQuery);
    }

    function _updateUsers() {
        var ordering;
        var filterQuery = '';

        ordering = vm.table.order.descending ? '-' + vm.table.order.column : vm.table.order.column;

        if (vm.table.statusFilter) {
            filterQuery = 'is_active:' + vm.table.statusFilter;
        }

        User.search({
            'filterquery': filterQuery,
            'page': vm.table.page - 1,
            'size': vm.table.pageSize,
            'sort': ordering,
            'q': vm.table.searchQuery,
        }, function(response) {
            vm.table.items = response.objects;
            vm.table.totalItems = response.total;
        }, function() {
            vm.table.items = [];
            vm.table.totalItems = 0;

            toastr.error('Could not load the user list, please try again later.', 'Error');
        });
    }

    function openTeamModal(user) {
        vm.user = user;

        if (vm.user.teams) {
            vm.teamList.forEach(function(team) {
                var selected = vm.user.teams.filter(function(teamId) {
                    return teamId === team.id;
                });

                team.selected = selected.length > 0;
            });
        }

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
            var form = '[name="userTeamForm"]';

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

    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }
}
