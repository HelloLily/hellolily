angular.module('app.directives').directive('editableSelect', editableSelect);

function editableSelect() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            type: '@',
            choiceField: '@',
            selectOptions: '=?', // contains any custom settings for the select
        },
        templateUrl: 'base/directives/editable_select.html',
        controller: EditableSelectController,
        controllerAs: 'es',
        transclude: true,
        bindToController: true,
    };
}

EditableSelectController.$inject = ['$filter', 'HLResource'];
function EditableSelectController($filter, HLResource) {
    var es = this;

    es.getChoices = getChoices;
    es.updateViewModel = updateViewModel;

    activate();

    /////

    function activate() {
        if (!es.selectOptions) {
            // If it's undefined just set it to an empty object.
            // Ensures we don't need extra checks in the code.
            es.selectOptions = {};
        }

        // Certain values in the given view model are objects,
        // so the default value in the select won't always work.
        // So check if it's an object and add .id.
        if (typeof es.viewModel[es.field] === 'object') {
            es.selectModel = es.viewModel[es.field].id;
        } else {
            es.selectModel = es.viewModel[es.field];
        }

        if (es.selectOptions.hasOwnProperty('display')) {
            es.optionDisplay = es.selectOptions.display;
        } else {
            es.optionDisplay = 'name';
        }
    }

    function getChoices() {
        var type;
        var field;

        if (es.selectOptions.hasOwnProperty('type')) {
            type = es.selectOptions.type;
        } else {
            type = es.type;
        }

        if (es.selectOptions.hasOwnProperty('field')) {
            field = es.selectOptions.field;
        } else {
            field = es.field;
        }

        var resourceCall = HLResource.getChoicesForField(type, field);

        // Add a return here so the select gets disabled while loading the options.
        return resourceCall.$promise.then(function(data) {
            if (data.hasOwnProperty('results')) {
                es.choices = data.results;
            } else {
                es.choices = data;
            }
        });
    }

    function updateViewModel($data) {
        // $data only contains the ID, so get the name from the choices in the scope.
        var selected = $filter('filter')(es.choices, {id: $data});

        if (es.choiceField) {
            es.viewModel[es.field] = $data;
            // Choice fields end with '_display',
            // so set the proper variable so front end changes are reflected properly.
            es.viewModel[es.field + '_display'] = selected.length ? selected[0].name : null;
        } else {
            es.viewModel[es.field] = selected.length ? selected[0] : null;
        }

        var args = {
            id: es.viewModel.id,
        };

        args[es.field] = $data;

        return HLResource.patch(es.type, args).$promise;
    }
}
