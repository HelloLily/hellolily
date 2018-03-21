function UserAvatarController() {
    const ACTIVE_TIME = 5;
    const AWAY_TIME = 15;
    const UNAVAILABLE_TIME = 120;
    const ctrl = this;

    ctrl.getActivityState = () => {
        let status = null;

        if (ctrl.user.last_activity) {
            const diff = Math.abs(new Date(ctrl.user.last_activity) - new Date());
            const minutes = Math.floor((diff / 1000) / 60);

            if (minutes <= ACTIVE_TIME) {
                status = 0;
            } else if (minutes > ACTIVE_TIME && minutes <= AWAY_TIME) {
                status = 1;
            } else if (minutes > AWAY_TIME && minutes <= UNAVAILABLE_TIME) {
                status = 2;
            }
        }

        return status;
    };
}

angular.module('app.directives').component('userAvatar', {
    templateUrl: 'base/directives/user_avatar.html',
    controller: UserAvatarController,
    bindings: {
        user: '<',
    },
    transclude: true,
});
