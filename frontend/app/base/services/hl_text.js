angular.module('app.services').service('HLText', HLText);
function HLText() {
    /**
     * hlCapitalize() lowercases the whole string and makes the first character uppercase
     * This means 'STRING' becomes 'String'
     *
     * @returns (string): returns a string with only the first character uppercased
     */
    String.prototype.hlCapitalize = function() {
        var newString = this.toLowerCase();
        return newString.charAt(0).toUpperCase() + newString.substring(1);
    };
}
