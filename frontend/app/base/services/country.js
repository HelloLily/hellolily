angular.module('app.services').factory('Country', Country);

Country.$inject = ['$q', 'Account'];
function Country($q, Account) {
    var list = [];

    var Country = {};

    Country.getList = getList;

    activate();

    ////

    function activate() {
        getList();
    }

    function getList() {
        var deferred = $q.defer();
        if (list.length) {
            deferred.resolve(list);
        } else {
            // Fetch the country choices from Address model
            Account.addressOptions(function (data) {
                list = data.actions.POST.country.choices;
                deferred.resolve(list);
            });
        }

        return deferred.promise;
    }

    return Country
}
