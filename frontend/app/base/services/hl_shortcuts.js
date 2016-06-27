angular.module('app.services').service('HLShortcuts', HLShortcuts);

HLShortcuts.$inject = ['$state', '$timeout', '$rootScope'];
function HLShortcuts($state, $timeout, $rootScope) {
    // Use $rootScope because $root is unavailable in services.
    // This watches the change in states so we can execute certain Mousetrap
    // functions on specific pages.
    $rootScope.$on('$stateChangeSuccess', function() {
        if ($state.current.name === 'base.email.list') {
            Mousetrap.bind('c', function() {
                $state.go('base.email.compose');
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('c');
            });
        }

        if ($state.current.name === 'base.email.detail') {
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

            Mousetrap.bind('d', function() {
                // Broadcast event for email/controllers/detail.js to handle
                // sending the particular email to trash.
                $rootScope.$broadcast('deleteMessageByShortCode');
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('d');
            });

            Mousetrap.bind('e', function() {
                // Broadcast event for email/controllers/detail.js to handle
                // sending the particular email to trash.
                $rootScope.$broadcast('archiveMessageByShortCode');
                // Unbind after pressed so next bind can take place.
                Mousetrap.unbind('e');
            });
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
                    if ($state.current.name === 'base.contacts') {
                        scope.table.filter = '';

                        // TODO: Remove else if statement if we refactor code to
                        // make the filter/search model consistent.
                    } else if ($state.current.name === 'base.deals' || $state.current.name === 'base.cases') {
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
