angular.module('app.directives').directive('editableRelated', editableRelated);

function editableRelated() {
    return {
        restrict: 'E',
        scope: {
            model: '=',
            type: '@',
            field: '@',
        },
        templateUrl: function(elem, attrs) {
            return 'base/directives/editable_' + attrs.field + '.html';
        },
        controller: EditableRelatedController,
        controllerAs: 'er',
        transclude: true,
        bindToController: true,
        link: function(scope, element, attr) {
            // Bind click event to the current directive.
            element.on('click', '.js-edit', function() {
                scope.er.showForm();
                scope.$apply();
            });

            element.on('click', '.js-add', function() {
                scope.er.showForm(true);
                scope.$apply();
            });
        },
    };
}

EditableRelatedController.$inject = ['HLFields', 'HLResource', 'HLUtils'];
function EditableRelatedController(HLFields, HLResource, HLUtils) {
    var er = this;
    er.formVisible = false;

    er.addRelatedField = addRelatedField;
    er.removeRelatedField = removeRelatedField;
    er.closeForm = closeForm;
    er.submit = submit;
    er.showForm = showForm;

    // TODO: LILY-1520: Clean up this model specific code.
    er.formatPhoneNumber = HLUtils.formatPhoneNumber;
    er.setPrimaryEmailAddress = HLUtils.setPrimaryEmailAddress;

    er.telephoneTypes = [
        {key: 'work', value: 'Work'},
        {key: 'mobile', value: 'Mobile'},
        {key: 'home', value: 'Home'},
        {key: 'fax', value: 'Fax'},
        {key: 'other', value: 'Other'},
    ];

    er.addressTypes = [
        {key: 'visiting', value: 'Visiting address'},
        {key: 'billing', value: 'Billing address'},
        {key: 'shipping', value: 'Shipping address'},
        {key: 'home', value: 'Home address'},
        {key: 'other', value: 'Other'},
    ];

    activate();

    /////

    function activate() {
        er.items = er.model[er.field];
        // Store the original items in case we cancel the editing.
        er.originalItems = angular.copy(er.items);

        er.formName = er.field + 'Form';
    }

    function addRelatedField() {
        // Default status is 'Other'.
        var status = 1;
        var isPrimary = false;

        switch (er.field) {
            case 'email_addresses':
                if (er.items.length === 0) {
                    // No email addresses added yet, so first one is primary.
                    status = 2;
                    isPrimary = true;
                }

                er.items.unshift({is_primary: isPrimary, status: status});
                break;
            case 'phone_numbers':
                er.items.unshift({type: 'work'});
                break;
            case 'addresses':
                er.items.unshift({type: 'visiting'});
                break;
            case 'websites':
                er.items.unshift({website: '', is_primary: false});
                break;
            default:
                break;
        }
    }

    function removeRelatedField(item) {
        item.is_deleted = !item.is_deleted;
    }

    function submit() {
        var element = '[name="' + er.formName + '"]';

        var args = {
            id: er.model.id,
        };

        args[er.field] = HLFields.cleanInlineRelatedFields(er.items);

        HLUtils.blockUI(element, true);

        return HLResource.patch(er.type, args).$promise.then(function(response) {
            er.formVisible = false;
            er.items = response[er.field];

            HLUtils.unblockUI(element);
        }).catch(function() {
            HLUtils.unblockUI(element);
        });
    }

    function showForm(add) {
        er.formVisible = true;

        if (!er.items.length || add) {
            er.addRelatedField();
        }
    }

    function closeForm() {
        // Cancel the editing and restore the original values.
        angular.copy(er.originalItems, er.items);
        er.formVisible = false;
    }
}
