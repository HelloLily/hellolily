angular.module('app.dashboard.directives').directive('usersFilter', usersFilter);

function usersFilter() {
    return {
        restrict: 'E',
        scope: {
            usersStore: '=',
            storageName: '=',
            allowEmpty: '=',
        },
        templateUrl: 'dashboard/directives/users_filter.html',
        controller: UsersFilterController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

UsersFilterController.$inject = ['LocalStorage', 'UserTeams'];
function UsersFilterController(LocalStorage, UserTeams) {
    var vm = this;
    var storage = LocalStorage(vm.storageName);

    vm.usersSelection = storage.get('usersFilter', [currentUser.id]);
    vm.usersDisplayNames = storage.get('usersDisplayFilter', [currentUser.firstName]);
    vm.teamsSelection = storage.get('teamsFilter', []);
    vm.currentUser = currentUser;
    vm.users = [];
    vm.teams = [];

    vm.toggleUser = toggleUser;
    vm.loadTeams = loadTeams;

    function loadTeams() {
        var teamObj;
        var userObj;
        var users;
        var ownTeam;
        var teams;

        UserTeams.query(function(response) {
            teams = [];

            angular.forEach(response.results, function(team) {
                if (team && team.users.length) {
                    users = [];
                    ownTeam = false;

                    angular.forEach(team.users, function(user) {
                        // Create a user object.
                        userObj = {
                            id: user.id,
                            full_name: user.full_name,
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

            vm.teams = teams;
        });
    }

    function toggleUser(team, userId) {
        var selectionIndex;
        var selectedFilter = [];
        var filter;

        if (userId) {
            selectionIndex = vm.usersSelection.indexOf(userId);

            // If the selected id is already in the array remove it.
            // Otherwise add it to the selected users.
            if (selectionIndex > -1) {
                vm.usersSelection.splice(selectionIndex, 1);
            } else {
                vm.usersSelection.push(userId);
            }

            // If the selected id is the same as the currentUser.
            // Check to see if the user needs to be removed from the
            // names to display.
            if (userId === currentUser.id) {
                if (selectionIndex > -1) {
                    vm.usersDisplayNames.splice(selectionIndex, 1);
                } else {
                    vm.usersDisplayNames.push(currentUser.fullName);
                }
            }

            //
            if (vm.teamsSelection.indexOf(team.id) > -1) {
                vm.teamsSelection.splice(vm.teamsSelection.indexOf(team.id), 1);
            }
        } else {
            selectionIndex = vm.teamsSelection.indexOf(team.id);

            // If the selected team id is already in the array remove it.
            // Otherwise add it to the array.
            if (selectionIndex > -1) {
                vm.teamsSelection.splice(selectionIndex, 1);
            } else {
                vm.teamsSelection.push(team.id);
            }

            // Loop through the teams to see if the user needs to be removed
            // from the selected users array.
            angular.forEach(vm.teams, function(teams) {
                if (teams.id === team.id) {
                    angular.forEach(teams.users, function(users) {
                        var userIdx = vm.usersSelection.indexOf(users.id);

                        if (selectionIndex > -1) {
                            if (userIdx > -1) {
                                vm.usersSelection.splice(userIdx, 1);
                            }
                        } else {
                            if (userIdx <= -1) {
                                vm.usersSelection.push(users.id);
                            }
                        }
                    });
                }
            });
        }

        if (!vm.allowEmpty) {
            // When everyone is unselected add the currentUser to the selection.
            if (vm.usersSelection.length === 0) {
                vm.usersSelection.unshift(currentUser.id);
            }
        }

        // Generate the names to display for the selected users.
        vm.usersDisplayNames = [];
        angular.forEach(vm.teams, function(teams) {
            angular.forEach(teams.users, function(user) {
                // User is selected, but hasn't been added to the displayed names yet.
                if (vm.usersSelection.indexOf(user.id) > -1 && vm.usersDisplayNames.indexOf(user.full_name) === -1) {
                    vm.usersDisplayNames.push(user.full_name);
                }
            });
        });

        // Check if the currentUser is in the selection at the
        // first name to the names to display.
        if (vm.usersSelection.indexOf(currentUser.id) > -1) {
            vm.usersDisplayNames.push(currentUser.fullName);
        }

        // Generate elastic search string.
        angular.forEach(vm.usersSelection, function(id) {
            selectedFilter.push('assigned_to_id:' + id);
        });

        angular.forEach(vm.teamsSelection, function(id) {
            selectedFilter.push('assigned_to_groups:' + id);
        });

        filter = selectedFilter.join(' OR ');

        // Put stuff in the local storage.
        storage.put('usersFilter', vm.usersSelection);
        storage.put('usersDisplayFilter', vm.usersDisplayNames);
        storage.put('teamsFilter', vm.teamsSelection);

        vm.usersStore = filter;
    }
}
