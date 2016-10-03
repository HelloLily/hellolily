angular.module('app.users.filters').filter('fullName', fullName);

function fullName() {
    return function(user) {
        return [user.first_name, user.last_name].join(' ');
    };
}
