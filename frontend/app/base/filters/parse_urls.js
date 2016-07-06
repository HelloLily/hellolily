var Autolinker = require('autolinker');

/**
 * parseUrls is a template filter to call Autolinker.
 * This is a library which automatically detects links, email addresses and
 * Twitter handles and converts them to clickable links.
 *
 * @param text {string}: Text to be converted
 *
 * @returns: string: Text containing clickable links.
 */
angular.module('app.filters').filter('parseUrls', parseUrls);

parseUrls.$inject = [];
function parseUrls() {
    return function(text) {
        return Autolinker.link(text, {
            replaceFn: function(autolinker, match) {
                var email;

                switch (match.getType()) {
                    case 'email':
                        email = match.getEmail();
                        return '<a href="#/email/compose/' + email + '/">' + email + '</a>';
                    default:
                        return true;
                }
            },
        });
    };
}
