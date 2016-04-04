/**
 * Custom Sanitize checks if specific HTML tags are met and marks them as invalid.
 * This function prevents $sce to mark custom tags as invalid.
 * i.e. things as <SIP-234893> are normally marked unsafe by $sce, we want to
 * allow users to use these as they wish.
 *
 * @param text {string}: Text inputted by using this filter.
 */
angular.module('app.filters').filter('customSanitize', customSanitize);

customSanitize.$inject = ['$sce'];
function customSanitize($sce) {
    return function(text) {
        var replacer = /<script[^>]*>([\S\s]*?)<\/script>?|<video[^>]*>.*(<\/?video>?)?|<head[^>]*>.*(<\/?head>?)?|<img[^>]*>.*(<\/?img>?)?|<iframe[^>]*>.*(<\/?iframe>?)?|<audio[^>]*>.*(<\/?audio>?)?|<object[^>]*>.*(<\/?object>?)?|<style[^>]*>.*(<\/?style>?)?/g;
        var stripped = text.replace(replacer, '');
        return $sce.trustAsHtml(stripped);
    };
}
