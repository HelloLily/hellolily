angular.module('app.directives').directive('editableRelated', editableRelated);

function editableRelated() {
    return {
        restrict: 'E',
        scope: {
            model: '=',
            type: '@',
            field: '@',
        },
        templateUrl: (elem, attrs) => {
            return `base/directives/editable_${attrs.field}.html`;
        },
        controller: EditableRelatedController,
        controllerAs: 'er',
        transclude: true,
        bindToController: true,
        link: (scope, element, attr) => {
            // Bind click event to the current directive.
            element.on('click', '.js-edit', () => {
                scope.er.showForm();
            });

            element.on('click', '.js-add', () => {
                scope.er.showForm(true);
            });

            element.on('click', '.editable', event => {
                const selection = window.getSelection().toString();

                const elementName = event.originalEvent.target.localName;

                // Don't open the edit form if we're clicking a link.
                if (!selection && elementName !== 'a') {
                    scope.er.showForm();
                }
            });
        },
    };
}

EditableRelatedController.$inject = ['$scope', 'HLFields', 'HLResource', 'HLUtils'];
function EditableRelatedController($scope, HLFields, HLResource, HLUtils) {
    let er = this;
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
        let status = 1;
        let isPrimary = false;

        switch (er.field) {
            case 'email_addresses':
                if (er.items.length === 0) {
                    // No email addresses added yet, so first one is primary.
                    status = 2;
                    isPrimary = true;
                }

                er.items.push({is_primary: isPrimary, status});
                break;
            case 'phone_numbers':
                er.items.push({type: 'work'});
                break;
            case 'addresses':
                er.items.push({type: 'visiting'});
                break;
            case 'websites':
                er.items.push({website: '', is_primary: false});
                break;
            default:
                break;
        }
    }

    function removeRelatedField(item) {
        item.is_deleted = !item.is_deleted;
    }

    function submit() {
        const element = `[name="${er.formName}"]`;

        let args = {
            id: er.model.id,
        };

        args[er.field] = HLFields.cleanInlineRelatedFields(er.items);

        HLUtils.blockUI(element, true);

        return HLResource.patch(er.type, args).$promise.then(response => {
            er.formVisible = false;
            er.items = response[er.field];

            HLUtils.unblockUI(element);
        }).catch(() => {
            HLUtils.unblockUI(element);
        });
    }

    function showForm(add) {
        er.formVisible = true;

        if (!er.items.length || add) {
            er.addRelatedField();
        }

        $scope.$apply();
    }

    function closeForm() {
        // Cancel the editing and restore the original values.
        er.formVisible = false;
        angular.copy(er.originalItems, er.items);
    }
}
