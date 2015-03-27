var UserFilters = angular.module('UserFilters', []);

UserFilters.filter('fullName', function() {
    return function(user) {
        return [user.first_name, user.preposition, user.last_name].join(' ');
    };
});
