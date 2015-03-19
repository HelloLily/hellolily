$(function() {
    // Provide fake gettext for when it is not available, for example during development
    if( typeof gettext !== 'function' ) {
        window.gettext = function (text) {
            return text;
        };
    }
});
