angular.module('app.services').factory('Settings', ['LocalStorage', function() {
    let page = new Page(...arguments);
    return {
        page: page,
        email: page.email,
    };
}]);

/**
 * Class representing the main settings object for the email sidebar layout.
 */
class Sidebar {
    constructor() {
        this.account = null;
        this.contact = null;
        this.cases = null;
        this.deals = null;
        this.form = null;
        this.isVisible = false;
    }
}

/**
 * Class representing the main settings object for email layout.
 */
class Email {
    /**
     * Initialize email layout.
     * @param {LocalStorage} storage - LocalStorage instance.
     */
    constructor(storage) {
        this.sidebar = new Sidebar();
        this.storage = storage;
        this.title = 'Welcome';
        this.previousInbox = this.storage.get('previousInbox', null);
        this.page = 0;
    }

    /**
     * Set previous email state.
     * @param {Object} previousInbox - Email state object.
     */
    setPreviousInbox(previousInbox) {
        this.storage.put('previousInbox', previousInbox);
        this.previousInbox = previousInbox;
    }

    /**
     * Reset all the data properties that concern the email layout.
     */
    resetEmailSettings() {
        // email.sidebar stores the state of sidebar panels (so hidden/closed).
        this.sidebar = {
            account: null,
            contact: null,
            case: null,
            deal: null,
            form: null,
            isVisible: false,
        };

        // email.data stores the actual data which is used for the sidebars.
        this.data = {
            website: null,
            account: null,
            contact: null,
            cases: null,
            deals: null,
        };
    }
}

/**
 * Class representing the main settings object for page header layout.
 */
class Header {
    constructor() {
        this.main = 'Lily';
    }

    /**
     * Sets the header's main title.
     * @param {String} pageType - The page category/type, e.g. `custom`/list`/`create`.
     * @param {String} newHeader - The new name to use in the title.
     * @return {String} The new title.
     */
    setMain(pageType, newHeader) {
        var formats = {
            create: 'New ',
            edit: 'Edit ',
            custom: '',
        };

        if (pageType && newHeader) {
            if (formats[pageType]) {
                this.main = formats[pageType] + newHeader;
            } else {
                this.main = newHeader.charAt(0).toUpperCase() + newHeader.slice(1);
            }
        }
    }
}

class Toolbar {
    constructor() {
        this.data = null;
    }
}

/**
 * Class representing the main settings object for page layout.
 */
class Page {
    constructor(localStorage) {
        this.storage = localStorage('generalSettings');
        this.title = 'Welcome';

        this.email = new Email(this.storage);
        this.header = new Header();
        this.toolbar = new Toolbar();
        this.previousState = null;
    }

    /**
     * Sets tab/window border title, but also the header's title and (optional)
     * context of contact/account.
     * @param {String} pageType - The page category/type, e.g. `custom`/list`/`create`.
     * @param {String} objectInfo - The type of objects the page shows, e.g. `accounts`/`contacts`.
     * @param {Contact} contact - A contact object to set the page context to.
     * @param {Account} account - An account object to set the page context to.
     */
    setAllTitles(pageType, objectInfo, contact = null, account = null) {
        // Make sure sidebar forms don't set the titles/headers.
        if (!this.email.sidebar.form) {
            this.title = objectInfo.charAt(0).toUpperCase() + objectInfo.slice(1);
            this.header.setMain(pageType, objectInfo);
            this.contact = contact;
            this.account = account;
        }
    }
}
