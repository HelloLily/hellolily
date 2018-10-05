angular.module('app.integrations').config(quoteConfig);

quoteConfig.$inject = ['$stateProvider'];
function quoteConfig($stateProvider) {
    $stateProvider.state('base.integrations.pandadoc.quotes', {
        url: '/quotes',
    });

    $stateProvider.state('base.integrations.pandadoc.quotes.create', {
        url: '/create/{dealId:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'integrations/controllers/quote_form.html',
                controller: QuoteCreateController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Create',
        },
        resolve: {
            currentDeal: ['Deal', '$stateParams', function(Deal, $stateParams) {
                var id = $stateParams.dealId;
                return Deal.get({id: id}).$promise;
            }],
            dealContact: ['Contact', 'currentDeal', function(Contact, currentDeal) {
                var contact;

                if (currentDeal.contact) {
                    contact = Contact.get({id: currentDeal.contact.id}).$promise;
                }

                return contact;
            }],
            tenant: ['Tenant', function(Tenant) {
                return Tenant.query({}).$promise;
            }],
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.integrations').controller('QuoteCreateController', QuoteCreateController);

QuoteCreateController.$inject = ['$http', '$timeout', 'Settings', 'currentDeal', 'dealContact', 'tenant', 'user'];
function QuoteCreateController($http, $timeout, Settings, currentDeal, dealContact, tenant, user) {
    var vm = this;

    vm.deal = currentDeal;
    vm.deal.contact = dealContact;
    vm.tenant = tenant;
    vm.currentUser = user;

    vm.openPandaDoc = openPandaDoc;

    activate();

    //////

    function activate() {
        Settings.page.setAllTitles('create', 'quote');

        openPandaDoc();
    }

    function openPandaDoc() {
        var account;
        var address;
        var editor = new PandaDoc.DocEditor();
        var recipients = [{
            'first_name': vm.currentUser.first_name,
            'last_name': vm.currentUser.last_name,
            'email': vm.currentUser.email,
            'roleName': 'User',
        }];
        var docName;

        // Setup up the template variables.
        var tokens = {
            // Current user's info.
            'User.FirstName': vm.currentUser.first_name,
            'User.LastName': vm.currentUser.last_name,
            'User.EmailAddress': vm.currentUser.email,
            'User.PhoneNumber': vm.currentUser.phone_number,
            'Date': moment().format('DD/MM/YYYY'),
        };

        if (vm.deal.contact) {
            tokens['Client.FirstName'] = vm.deal.contact.first_name;
            tokens['Client.LastName'] = vm.deal.contact.last_name;

            recipients.push({
                'first_name': vm.deal.contact.first_name,
                'last_name': vm.deal.contact.last_name,
                'roleName': 'Client',
            });

            if (vm.deal.contact.email_addresses.length) {
                tokens['Client.Email'] = vm.deal.contact.email_addresses[0].email_address;

                recipients[1].email = vm.deal.contact.email_addresses[0].email_address;
            }

            if (vm.deal.account) {
                account = vm.deal.account;
            } else if (vm.deal.contact.accounts.length) {
                account = vm.deal.contact.accounts[0];
            }

            if (account) {
                tokens['Client.Company'] = account.name;

                if (account.addresses.length) {
                    address = account.addresses[0];

                    tokens['Client.Address'] = address.address;
                    tokens['Client.PostalCode'] = address.postal_code;
                    tokens['Client.City'] = address.city;
                }

                docName = account.name;
            }
        }

        editor.show({
            el: '.hl-form-body',
            cssClass: 'pandadoc-form',
            data: {
                docName: docName,
                tokens: tokens,
                recipients: recipients,
                metadata: {
                    'deal': vm.deal.id,
                    'account': account.id || null,
                    'user': vm.currentUser.id,
                },
            },
            events: {
                onDocumentCreated: saveDocument,
            },
        });
    }

    function saveDocument(data) {
        $http({
            method: 'POST',
            url: `/api/integrations/documents/${vm.deal.id}/`,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            data: `document_id=${data.document.id}&contact_id=${vm.deal.contact.id}`,
        });
    }
}
