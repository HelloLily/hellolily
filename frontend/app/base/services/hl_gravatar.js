angular.module('app.services').service('HLGravatar', HLGravatar);

function HLGravatar() {
    this.getGravatar = function(email) {
        var trimmedEmail = email.trim();
        var lowerCasedEmail = trimmedEmail.toLowerCase();
        var gravatarHash = md5(lowerCasedEmail);

        return 'https://secure.gravatar.com/avatar/' + gravatarHash + '?s=200&d=mm';
    };
}
