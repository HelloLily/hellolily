$(document).ready(function() {
   $('.formset').formset();

   $('body').on('formDeleted', '[data-formset-form]', function() {
       $(this).stop().slideDown();
       $(this).find(':input:enabled:visible').attr('data-formset-disabled', true).attr('readonly', 'readonly');
       $(this).find('[data-formset-delete-button]').toggleClass('hidden');
       $(this).find('[data-formset-undo-delete]').toggleClass('hidden');
   });

    $('[data-formset-undo-delete]').live('click', function() {
        var formset = $(this).closest('[data-formset-form]');

        formset.find('[data-formset-disabled=true]').removeAttr('data-formset-disabled').removeAttr('readonly');
        formset.find('input[name$="DELETE"]').attr('checked', false).change();
        formset.find('[data-formset-delete-button]').toggleClass('hidden');
        $(this).toggleClass('hidden');
    });
});