angular.module('app.email.services').factory('EmailAccount', EmailAccount);

EmailAccount.$inject = ['$resource'];
function EmailAccount($resource) {
    var _emailAccount = $resource(
        '/api/messaging/email/accounts/:id/',
        null,
        {
            get: {
                transformResponse: data => {
                    let account = angular.fromJson(data);

                    account.shared_email_configs = _emailAccount.filterEmailConfigs(account);

                    return account;
                },
            },
            query: {
                isArray: false,
                transformResponse: data => {
                    let accounts = angular.fromJson(data);

                    if (accounts.results && accounts.results.length) {
                        accounts.results.map(account => {
                            account.is_public = (account.privacy === _emailAccount.PUBLIC);
                            account.shared_email_configs = _emailAccount.filterEmailConfigs(account);
                        });
                    }

                    return accounts;
                },
            },
            update: {
                method: 'PUT',
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            mine: {
                method: 'GET',
                url: '/api/messaging/email/accounts/mine/',
                isArray: true,
            },
            cancel: {
                method: 'DELETE',
                url: '/api/messaging/email/accounts/:id/cancel',
                params: {
                    id: '@id',
                },
            },
        }
    );

    _emailAccount.getPrivacyOptions = getPrivacyOptions;
    _emailAccount.filterEmailConfigs = filterEmailConfigs;

    _emailAccount.PUBLIC = 0;
    _emailAccount.READONLY = 1;
    _emailAccount.METADATA = 2;
    _emailAccount.PRIVATE = 3;

    /////////

    function getPrivacyOptions() {
        // Hardcoded because these are the only privacy options.
        return [
            {id: 0, name: 'Group inbox', text: 'Used by multiple people'},
            {id: 1, name: 'Public personal inbox', text: 'Colleagues can see my email'},
            {id: 2, name: 'Personal inbox, with shared metadata', text: 'The content of email is hidden, only meta data is visible'},
            {id: 3, name: 'Private inbox', text: 'Nothing is shared, you lose Lily superpowers'},
        ];
    }

    function filterEmailConfigs(account) {
        var configs = [];

        if (account.shared_email_configs && account.shared_email_configs.length) {
            // Filter out the email configuration for the user's own account.
            account.shared_email_configs.map(config => {
                if (account.owner.id !== config.user) {
                    configs.push(config);
                }
            });
        }

        return configs;
    }

    return _emailAccount;
}
