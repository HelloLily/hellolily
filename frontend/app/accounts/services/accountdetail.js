angular.module('app.accounts.services').factory('AccountDetail', AccountDetail);

AccountDetail.$inject = ['$resource', 'HLObjectDetails'];
function AccountDetail($resource, HLObjectDetails) {
    return $resource(
        '/search/search/?type=accounts_account&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var account = data.hits[0];
                        account.phone = HLObjectDetails.getPhone(account);
                        account.phones = HLObjectDetails.getPhones(account);
                        account.email_address = HLObjectDetails.getEmailAddresses(account);

                        return account;
                    }

                    return null;
                },
            },
        }
    );
}
