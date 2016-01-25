angular.module('app.services').factory('Settings', Settings);

Settings.$inject = [];
function Settings() {
    var Settings = {
        page: {
            title: 'Welcome',
            setTitle: setTitle,  // unfortunately because of js + angular we must use ugly setters.
            header: {
                main: 'Hellolily',
                setMain: setMain,
                sub: 'welcome to my humble abode',
                setSub: setSub,
            },
            setAllTitles: setAllTitles,
        },
        email: {
            sidebar: {
                account: null,
                contact: null,
                cases: null,
                form: null,
                isVisible: false,
            },
            resetEmailSettings: resetEmailSettings,
        },
    };

    function setTitle(pageType, newTitle) {
        // Capitalize first letter of the new title.
        Settings.page.title = newTitle.charAt(0).toUpperCase() + newTitle.slice(1);

        return Settings.page.title;
    }

    function setMain(pageType, newHeader) {
        var formats = {
            create: 'New ',
            edit: 'Edit ',
            custom: '',
        };

        if (pageType && newHeader) {
            if (formats[pageType]) {
                Settings.page.header.main = formats[pageType] + newHeader;
            } else {
                Settings.page.header.main = newHeader.charAt(0).toUpperCase() + newHeader.slice(1);
            }
        }

        return Settings.page.header.main;
    }

    function setSub(pageType, newHeader) {
        var formats = {
            list: 'do all your lookin\' here',
            detail: 'the devil is in the details',
            create: 'everything has to start somewhere',
            edit: 'change is natural',
            email: 'sending love through the world',
            custom: '',
        };
        var _header = newHeader || '';

        if (pageType === 'custom') {
            Settings.page.header.sub = _header;
        } else {
            Settings.page.header.sub = formats[pageType];
        }

        return Settings.page.header.sub;
    }

    function setAllTitles(pageType, objectInfo) {
        setTitle(pageType, objectInfo);
        setMain(pageType, objectInfo);
        setSub(pageType, objectInfo);
    }

    function resetEmailSettings() {
        // email.sidebar stores the state of sidebar panels (so hidden/closed).
        Settings.email.sidebar = {
            account: null,
            contact: null,
            form: null,
            isVisible: false,
        };

        // email.data stores the actual data which is used for the sidebars.
        Settings.email.data = {
            website: null,
            account: null,
            contact: null,
            cases: null,
        };
    }

    return Settings;
}
