angular.module('app.services').service('HLShortcuts', HLShortcuts);

HLShortcuts.$inject = ['$state', '$timeout', '$rootScope', 'Settings'];
function HLShortcuts($state, $timeout, $rootScope, Settings) {
    // Use $rootScope because $root is unavailable in services.
    // This watches the change in states so we can execute certain Mousetrap
    // functions on specific pages.
    $rootScope.$on('$stateChangeSuccess', function() {
        var state = $state.current.name;
        if (state === 'base.email.list') {
            Mousetrap.bind('c', function() {
                $state.go('base.email.compose');
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('c');
            });
        }

        if (state === 'base.email.detail') {
            Mousetrap.bind('c', function() {
                _replyViaShortcode();
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('c');
            });

            Mousetrap.bind('r', function() {
                _replyViaShortcode();
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('r');
            });
        }

        if (state === 'base.email.compose') {
            Mousetrap.bind('mod+enter', function() {
                // Submit the email form.
                document.getElementById('fileupload').submit();
            });
        } else if (state === 'base.deals.detail.edit' || state === 'base.deals.create') {
            Mousetrap.bindGlobal('mod+enter', function() {
                // Broadcast event for deals/controllers/createupdate.js to save
                // the deal.
                $rootScope.$broadcast('saveDeal');
            }, 'keyup');
        } else if (state === 'base.cases.detail.edit' || state === 'base.cases.create') {
            Mousetrap.bindGlobal('mod+enter', function() {
                // Broadcast event for cases/controllers/createupdate.js to save
                // the case.
                $rootScope.$broadcast('saveCase');
            }, 'keyup');
        } else if (state === 'base.contacts.detail.edit' || state === 'base.contacts.create' ||
                   state === 'base.contacts.create.fromAccount') {
            Mousetrap.bindGlobal('mod+enter', function() {
                // Broadcast event for contact/controllers/createupdate.js to save
                // the contact.
                $rootScope.$broadcast('saveContact');
            });
        } else if (state === 'base.accounts.detail.edit' || state === 'base.accounts.create') {
            Mousetrap.bindGlobal('mod+enter', function() {
                // Broadcast event for account/controllers/createupdate.js to save
                // the account.
                $rootScope.$broadcast('saveAccount');
            });
        } else if (state === 'base.email.detail') {
            Mousetrap.bindGlobal('mod+enter', function() {
                // Broadcast event for account/controllers/createupdate.js to save
                // the account.
                if (Settings.email.sidebar.form === 'account') {
                    $rootScope.$broadcast('saveAccount');
                } else if (Settings.email.sidebar.form === 'contact') {
                    $rootScope.$broadcast('saveContact');
                }
            });
        } else {
            // Unbind when not a form page.
            Mousetrap.unbind('mod+enter');
        }

        // Function for both the c and r key when in Email Detail view.
        function _replyViaShortcode() {
            var message = $state.params.id;
            if (message) {
                $state.go('base.email.reply', {id: message});
            }
        }

        $timeout(function() {
            var searchField = '.hl-search-field';

            if (angular.element(searchField).length) {
                Mousetrap.bind('s', function() {
                    var scope = angular.element($(searchField).get(0)).scope();
                    angular.element(searchField).focus();
                    // TODO: Remove if statement if Contacts get refactored
                    // To utilize vm.table. instead of table.
                    if (state === 'base.contacts') {
                        scope.table.filter = '';

                        // TODO: Remove else if statement if we refactor code to
                        // make the filter/search model consistent.
                    } else if (state === 'base.deals' || state === 'base.cases') {
                        scope.vm.table.searchQuery = '';
                    } else {
                        scope.vm.table.filter = '';
                    }
                    scope.$apply();
                }, 'keyup');
            }
        });
    });
}
