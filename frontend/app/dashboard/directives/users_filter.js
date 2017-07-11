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
    var vm = this;
    var storage = new LocalStorage(vm.storageName);

    vm.storedNameDisplay = storage.get('nameDisplay', []);
    vm.storedTeamsSelection = storage.get('teamsSelection', []);
    vm.storedCurrentUserSelected = storage.get('currentUserSelected', false);
    vm.currentUser = currentUser;
    vm.teams = [];

    vm.toggleUser = toggleUser;
    vm.loadTeams = loadTeams;
    vm.toggleCollapsed = toggleCollapsed;

    activate();

    //////

    function activate() {
        $timeout(function() {
            loadTeams();

            vm.currentUser.selected = vm.storedCurrentUserSelected;
            vm.nameDisplay = vm.storedNameDisplay;
        }, 50);
    }

    function loadTeams() {
        UserTeams.query().$promise.then(function(response) {
            User.query({teams__isnull: 'True'}).$promise.then(function(userResponse) {
                var teamObj;
                var userObj;
                var users;
                var ownTeam;
                var unassignedUser;
                var teams = [];
                var unassignedTeam = {
                    users: [],
                    name: 'Not in team',
                    selected: false,
                    collapsed: true,
                };

                for (unassignedUser of userResponse.results) {
                    unassignedTeam.users.push(unassignedUser);
                }

                angular.forEach(response.results, function(team) {
                    if (team && team.users.length) {
                        users = [];
                        ownTeam = false;

                        angular.forEach(team.users, function(user) {
                            // Create a user object.
                            userObj = {
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
                        teamObj = {
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
                vm.storedTeamsSelection.map((storedTeam) => {
                    teams = teams.map((team) => {
                        if (storedTeam.id === team.id) {
                            team.selected = storedTeam.selected;
                            team.collapsed = storedTeam.collapsed;
                        }

                        // Loop through stored users and set current users to the state of the stored users.
                        storedTeam.users.map((storedUser) => {
                            team.users = team.users.map((user) => {
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

    function toggleUser(selectedTeam, selectedUser) {
        var selectedFilter = [];
        var names = [];
        var filter;

        if (selectedUser) {
            selectedUser.selected = !selectedUser.selected;

            if (selectedTeam) {
                selectedTeam.selected = false;
            }
        } else {
            selectedTeam.selected = !selectedTeam.selected;

            selectedTeam.users.map((teamUser) => {
                teamUser.selected = selectedTeam.selected;

                vm.teams.map((team) => {
                    if (team.id !== selectedTeam.id) {
                        team.users.map((user) => {
                            if (user.id === teamUser.id) {
                                user.selected = teamUser.selected;
                            }
                        });
                    }
                });
            });
        }

        vm.teams.map((team) => {
            // 'Not in team' isn't an actual team, so check for 'id' property.
            if (team.hasOwnProperty('id') && team.selected) {
                selectedFilter.push('assigned_to_teams.id:' + team.id);
            }

            team.users.map((user) => {
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
        filter = selectedFilter.join(' OR ');

        vm.nameDisplay = $filter('unique')(names);

        storage.put('nameDisplay', vm.nameDisplay);
        storage.put('teamsSelection', vm.teams);
        storage.put('currentUserSelected', vm.currentUser.selected);

        vm.usersStore = filter;
    }

    function toggleCollapsed(team) {
        team.collapsed = !team.collapsed;
        storage.put('teamsSelection', vm.teams);
    }
}
