angular.module('app.directives').component('archivedIndicator', {
    template: `
    <span ng-if="$ctrl.filter.isArchived" class="pull-right">
        <i class="fa fa-archive text-muted" uib-tooltip="{{ $root.messages.tooltips.filterArchived }}" tooltip-append-to-body="true"></i>
    </span>
    `,
    bindings: {
        filter: '<',
    },
});
