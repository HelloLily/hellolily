describe('app.accounts.list', function () {

    beforeEach(module('app.accounts'));

    var controller,
        AccountMock,
        scope;

    beforeEach(inject(function ($rootScope, _$controller_) {
        $controller = _$controller_;
        scope = $rootScope.$new();
        scope.conf = {};

        AccountMock = {
            delete: function(){}
        };

        controller = $controller('AccountList', {
            $scope: scope,
            Account: AccountMock
        });
    }));

    describe('deleteAccount', function () {
        it('Controller needs to have a function called deleteAccount', function () {
            expect(controller.deleteAccount).toBeDefined();
        });

        it('should show an confirm box and ask for permission to delete', function () {
            spyOn(AccountMock, 'delete');
            spyOn(window, 'confirm').and.returnValue(true);

            controller.deleteAccount({id:1});

            expect(window.confirm).toHaveBeenCalledWith('Are you sure?');

        });

        it('deleteAccount should call delete on AccountService', function () {
            spyOn(AccountMock, 'delete');
            spyOn(window, 'confirm').and.returnValue(true);

            controller.deleteAccount({id:1});

            expect(AccountMock.delete).toHaveBeenCalled();
        });
    });
});
