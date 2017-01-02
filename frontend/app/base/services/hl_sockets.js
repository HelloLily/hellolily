angular.module('app.services').service('HLSockets', HLSockets);

HLSockets.$inject = ['$state', '$timeout', '$rootScope', 'Settings'];
function HLSockets($state, $timeout, $rootScope, Settings) {
    const wsEnabled = 'WebSocket' in window &&
        'Notification' in window &&
        Notification.permission !== 'denied' &&
        currentUser.internalNumber;

    const listeners = {};
    let ws = null;

    if (wsEnabled) {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new ReconnectingWebSocket(wsScheme + '://' + window.location.host + '/');

        // Dispatch open and close events so these can be bound to.
        ws.onopen = () => this.dispatch('open');
        ws.onclose = () => this.dispatch('close');
        ws.onmessage = message => {
            const data = JSON.parse(message.data);
            this.dispatch(data.event, data.data);
        };
    }

    // Allow functions to bind to specific WebSocket events.
    this.bind = (type, callback) => {
        listeners[type] = listeners[type] || [];
        listeners[type].push(callback);
        return this;
    };

    this.close = (reason = '') => {
        if (wsEnabled) ws.close(1000, reason);
    };

    this.dispatch = (type, data = null) => {
        // Dispatches the event and its data to all functions bound to the event.
        if (!(type in listeners)) return;
        for (const callback of listeners[type]) {
            callback(data);
        }
    };
}
