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
                form: null,
                isVisible: false,
            },
            accountId: false,
            contactId: false,
        },
    };

    function setTitle(pageType, newTitle) {
        var formats = {
            list: 'List of ',
            detail: 'View ',
            create: 'New ',
            edit: 'Edit ',
            custom: '',
        };
        var _title = newTitle || '';

        if (pageType) {
            Settings.page.title = formats[pageType] + _title;
        }

        return Settings.page.title;
    }

    function setMain(pageType, newHeader) {
        var formats = {
            list: 'List of ',
            detail: 'View ',
            create: 'New ',
            edit: 'Edit ',
            custom: '',
        };

        if (pageType && newHeader) {
            Settings.page.header.main = formats[pageType] + newHeader;
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

    return Settings;
}
