angular.module('app.services').service('HLNotifications', HLNotifications);

HLNotifications.$inject = ['$state', 'LocalStorage', 'HLSockets'];
function HLNotifications($state, LocalStorage, HLSockets) {
    let sendNotification = false;

    _notificationWindowCheck();

    HLSockets.bind('notification', data => {
        _notificationWindowCheck();
        if (sendNotification && 'Notification' in window) {
            if (Notification.permission === 'granted') {
                _makeNotification(data);
            } else if (Notification.permission !== 'denied') {
                // If the user has not already accepted or denied notifications
                // permission will be asked to send the notification.
                Notification.requestPermission(function(permission) {
                    if (permission === 'granted') {
                        _makeNotification(data);
                    }
                });
            }
        }
    });

    function _makeNotification(data) {
        let notification;
        // If there is no name available, use the phone number in the title of the notification
        if (data.params.name !== '') {
            notification = new Notification(data.params.name + ' calling', {body: data.params.number, icon: data.icon});
        } else {
            notification = new Notification(data.params.number + ' calling', {body: '', icon: data.icon});
        }
        setTimeout(() => { notification.close(); }, 10000);
        ga('send', 'event', 'Caller info', 'Answer', 'Incoming call');
        notification.onclick = () => {
            switch (data.destination) {
                case 'account':
                    window.open($state.href('base.accounts.detail', {id: data.params.id}), '_blank');
                    break;
                case 'contact':
                    window.open($state.href('base.contacts.detail', {id: data.params.id}), '_blank');
                    break;
                case 'create':
                    // There is no way to know if an account or contact needs to be created. As it's more
                    // likely an account needs to be created, this links to account.create.
                    window.open($state.href('base.accounts.create', {
                        name: data.params.name,
                        phone_number: data.params.number,
                    }), '_blank');
                    break;
                default:
                    break;
            }
            notification.close();
            // Track clicking on the caller notification in Google analytics and Segment.
            ga('send', 'event', 'Caller info', 'Open', 'Popup');
            analytics.track('caller-notification-click', {
                'phone_number': data.params.number,
            });
        };
    }

    function _notificationWindowCheck() {
        // This function makes sure notifications are only shown once if
        // Lily is open in multiple windows/tabs.
        const storage = new LocalStorage('notificationWindow');
        let dateNow = new Date();
        let timestamp = storage.getObjectValue('timestamp', false);
        if (!timestamp || timestamp < dateNow.getTime() - 4000) {
            // The window sending the notifications will write a timestamp to localstorage
            // every second. When a notification is received and the timestamp is
            // older than 2 seconds, another window will take over.
            storage.putObjectValue('timestamp', dateNow.getTime());
            sendNotification = true;
            setInterval(() => {
                dateNow = new Date();
                storage.putObjectValue('timestamp', dateNow.getTime());
            }, 1000);
        }
    }
}
