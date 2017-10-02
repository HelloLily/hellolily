angular.module('app.dashboard.directives').directive('usersFilter', usersFilter);

function usersFilter() {
    return {
        restrict: 'E',
        scope: {
            usersStore: '=',
            storageName: '@',
        },
        templateUrl: 'dashboard/directives/users_filter.html',
        controller: UsersFilterController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

UsersFilterController.$inject = ['$filter', '$timeout', 'LocalStorage', 'User', 'UserTeams'];
function UsersFilterController($filter, $timeout, LocalStorage, User, UserTeams) {
    let vm = this;
    const storage = new LocalStorage(vm.storageName);

    vm.storedNameDisplay = storage.get('nameDisplay', []);
    vm.storedTeamsSelection = storage.get('teamsSelection', []);
    vm.storedCurrentUserSelected = storage.get('currentUserSelected', false);
    vm.currentUser = currentUser;
    vm.teams = [];

    vm.toggleUser = toggleUser;
    vm.loadTeams = loadTeams;
    vm.toggleCollapsed = toggleCollapsed;
    vm.hasSelection = hasSelection;

    activate();

    //////

    function activate() {
        $timeout(() => {
            loadTeams();

            vm.currentUser.selected = vm.storedCurrentUserSelected;
            vm.nameDisplay = vm.storedNameDisplay;
        }, 50);
    }

    function loadTeams() {
        UserTeams.query().$promise.then(response => {
            User.query({teams__isnull: 'True'}).$promise.then(userResponse => {
                let teams = [];
                const unassignedTeam = {
                    users: [],
                    name: 'Not in team',
                    selected: false,
                    collapsed: true,
                };

                for (let unassignedUser of userResponse.results) {
                    unassignedTeam.users.push(unassignedUser);
                }

                response.results.forEach(team => {
                    if (team && team.users.length) {
                        let users = [];
                        let ownTeam = false;

                        team.users.forEach(user => {
                            // Create a user object.
                            let userObj = {
                                id: user.id,
                                full_name: user.full_name,
                                selected: false,
                            };

                            // Do not add the current user to the users array.
                            if (currentUser.id === user.id) {
                                ownTeam = true;
                            } else {
                                users.push(userObj);
                            }
                        });

                        // Create a team object.
                        let teamObj = {
                            id: team.id,
                            name: team.name,
                            users: users,
                            collapsed: !ownTeam,
                            selected: false,
                        };

                        // If it is a team of the currentUser at that one
                        // to the top of the array.
                        if (ownTeam) {
                            teams.unshift(teamObj);
                        } else {
                            teams.push(teamObj);
                        }
                    }
                });

                if (unassignedTeam.users.length) {
                    teams.push(unassignedTeam);
                }

                // Loop through stored teams and set current teams to the state of the stored teams.
                vm.storedTeamsSelection.map(storedTeam => {
                    teams = teams.map(team => {
                        if (storedTeam.id === team.id) {
                            team.selected = storedTeam.selected;
                            team.collapsed = storedTeam.collapsed;
                        }

                        // Loop through stored users and set current users to the state of the stored users.
                        storedTeam.users.map(storedUser => {
                            team.users = team.users.map(user => {
                                if (storedUser.id === user.id) {
                                    user.selected = storedUser.selected;
                                }

                                return user;
                            });
                        });

                        return team;
                    });
                });

                vm.teams = teams;
            });
        });
    }

    function toggleUser(selectedTeam, selectedUser, toggleUsers = true) {
        if (selectedUser) {
            selectedUser.selected = !selectedUser.selected;

            if (selectedTeam) {
                selectedTeam.selected = false;
            }
        } else {
            if (toggleUsers) {
                selectedTeam.selected = !selectedTeam.selected;
                selectedTeam.filterOnTeam = selectedTeam.selected;

                selectedTeam.users.map(teamUser => {
                    teamUser.selected = selectedTeam.selected;

                    vm.teams.map(team => {
                        if (team.id !== selectedTeam.id) {
                            team.users.map(user => {
                                if (user.id === teamUser.id) {
                                    user.selected = teamUser.selected;
                                }
                            });
                        }
                    });
                });
            } else {
                selectedTeam.filterOnTeam = !selectedTeam.filterOnTeam;

                if (!selectedTeam.filterOnTeam && selectedTeam.selected) {
                    selectedTeam.selected = false;
                }
            }
        }

        let selectedFilter = [];
        let names = [];

        vm.teams.map(team => {
            // 'Not in team' isn't an actual team, so check for 'id' property.
            if (team.hasOwnProperty('id') && team.selected || team.filterOnTeam) {
                selectedFilter.push('assigned_to_teams:' + team.id);
            }

            team.users.map(user => {
                if (selectedUser && selectedUser.id === user.id) {
                    user.selected = selectedUser.selected;
                }

                if (user.selected) {
                    selectedFilter.push('assigned_to.id:' + user.id);
                    names.push(user.full_name);
                }
            });
        });

        if (vm.currentUser.selected) {
            selectedFilter.push('assigned_to.id:' + vm.currentUser.id);
            names.push(vm.currentUser.fullName);
        }

        selectedFilter = $filter('unique')(selectedFilter);

        const filter = selectedFilter.join(' OR ');

        vm.nameDisplay = $filter('unique')(names);

        storage.put('nameDisplay', vm.nameDisplay);
        storage.put('teamsSelection', vm.teams);
        storage.put('currentUserSelected', vm.currentUser.selected);

        vm.usersStore = filter;
    }

    function hasSelection(team) {
        // (!team.selected && (team.users | where: {selected: true}).length )
        if (!team.selected) {
            let selectedUserCount = team.users.reduce((count, user) => {
                return user.selected ? count + 1 : count;
            }, 0);

            if (selectedUserCount || team.filterOnTeam) {
                return true;
            }
        }

        return false;
    }

    function toggleCollapsed(team) {
        team.collapsed = !team.collapsed;
        storage.put('teamsSelection', vm.teams);
    }
}
