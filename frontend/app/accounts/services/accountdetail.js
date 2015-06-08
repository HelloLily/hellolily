angular.module('app.accounts.services').factory('AccountDetail', AccountDetail);

AccountDetail.$inject = ['$resource'];
function AccountDetail ($resource) {
    function getPhone(account) {
        if (account.phone_mobile) return account.phone_mobile[0];
        if (account.phone_work) return account.phone_work[0];
        if (account.phone_other) return account.phone_other[0];
        return '';
    }
    function getPhones(account) {
        var phones = [];
        if (account.phone_mobile) phones = phones.concat(account.phone_mobile);
        if (account.phone_work) phones = phones.concat(account.phone_work);
        if (account.phone_other) phones = phones.concat(account.phone_other);
        return phones;
    }
    return $resource(
        '/search/search/?type=accounts_account&filterquery=id\::id',
        {},
        {
            get: {
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    if (data && data.hits && data.hits.length > 0) {
                        var account = data.hits[0];
                        account.phone = getPhone(account);
                        account.phones = getPhones(account);
                        return account;
                    }
                    return null;
                }
            }
        }
    );
}
