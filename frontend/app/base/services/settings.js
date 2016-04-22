angular.module('app.services').factory('Settings', Settings);

Settings.$inject = ['LocalStorage'];
function Settings(LocalStorage) {
    var storage = LocalStorage('generalSettings');

    var _settings = {
        page: {
            title: 'Welcome',
            setTitle: setTitle,  // unfortunately because of js + angular we must use ugly setters.
            header: {
                main: 'Hellolily',
                setMain: setMain,
            },
            setAllTitles: setAllTitles,
            account: null,
            contact: null,
        },
        email: {
            sidebar: {
                account: null,
                contact: null,
                cases: null,
                deals: null,
                form: null,
                isVisible: false,
            },
            previousInbox: null,
            setPreviousInbox: setPreviousInbox,
            resetEmailSettings: resetEmailSettings,
        },
    };

    _settings.email.previousInbox = storage.get('previousInbox', null);

    function setTitle(pageType, newTitle) {
        // Capitalize first letter of the new title.
        _settings.page.title = newTitle.charAt(0).toUpperCase() + newTitle.slice(1);

        return _settings.page.title;
    }

    function setMain(pageType, newHeader) {
        var formats = {
            create: 'New ',
            edit: 'Edit ',
            custom: '',
        };

        if (pageType && newHeader) {
            if (formats[pageType]) {
                _settings.page.header.main = formats[pageType] + newHeader;
            } else {
                _settings.page.header.main = newHeader.charAt(0).toUpperCase() + newHeader.slice(1);
            }
        }

        return _settings.page.header.main;
    }


    function setAllTitles(pageType, objectInfo, contact, account) {
        // Make sure sidebar forms don't set the titles/headers.
        if (!_settings.email.sidebar.form) {
            setTitle(pageType, objectInfo);
            setMain(pageType, objectInfo);
            _settings.page.contact = contact;
            _settings.page.account = account;
        }
    }

    function resetEmailSettings() {
        // email.sidebar stores the state of sidebar panels (so hidden/closed).
        _settings.email.sidebar = {
            account: null,
            contact: null,
            case: null,
            deal: null,
            form: null,
            isVisible: false,
        };

        // email.data stores the actual data which is used for the sidebars.
        _settings.email.data = {
            website: null,
            account: null,
            contact: null,
            cases: null,
            deals: null,
        };
    }

    function setPreviousInbox(previousInbox) {
        storage.put('previousInbox', previousInbox);

        _settings.email.previousInbox = previousInbox;
    }

    return _settings;
}
