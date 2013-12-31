/**
 * Lily Formset 1.0
 * @author Allard Stijnman, Cornelis Poppema (Voys Telecom)
 * @requires jQuery 1.2.6 or later
 *
 * Original source: django dynamic formset
 * See: http://code.google.com/p/django-dynamic-formset/
 */

;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp('(' + prefix + '-\\d+)'),
                    replacement = prefix + '-' + ndx;
                if (elem.attr('for')) elem.attr('for', elem.attr('for').replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name') && idRegex.test(elem.attr('name'))) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
                if (elem.attr('value') && idRegex.test(elem.attr('value'))) elem.attr('value', elem.attr('value').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find('input,select,textarea,label').length > 0;
            },

            preventEmptyFormset = function(row, forms) {
                var deleteTriggers, buttonTrigger;
                if (options.preventEmptyFormset && forms.length === 1) {
                    // Prevent the last form from being deleted:
                    deleteTriggers = forms.find('.' + options.deleteCssClass).not('.dont');
                    for (var i = 0, triggerCount = deleteTriggers.length; i < triggerCount; i++) {
                        if ((buttonTrigger = $(deleteTriggers[i])) != undefined) {
                            $(buttonTrigger).parent().addClass('hidden');
                        }
                    }
                } else {
                    // Make sure that delete on first form is enabled:
                    deleteTriggers = $(forms[0]).find('.' + options.deleteCssClass).not('.dont');
                    for (var i = 0, triggerCount = deleteTriggers.length; i < triggerCount; i++) {
                        if ((buttonTrigger = $(deleteTriggers[i])) !== undefined) {
                            $(buttonTrigger).parent().removeClass('hidden');
                        }
                    }
                }
            },

            insertDeleteLink = function(row) {
                row.find('.' + options.deleteCssClass).not('.dont').click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input[id $= "-DELETE"]').not(':visible');
                    if (del.length) {
                        // We're dealing with an inline formset; rather than remove
                        // this form from the DOM, we'll mark it as deleted and hide
                        // it, then let Django handle the deleting:
                        del.val('on');
                        row.hide();
                    } else {
                        row.remove();
                        // Update the TOTAL_FORMS form count.
                        // Also update names and IDs for all remaining form controls so they remain in sequence:
                        var forms = $('.' + options.formCssClass).not('.formset-custom-template');
                        $('#id_' + options.prefix + '-TOTAL_FORMS').val(forms.length);
                        for (var i=0, formCount=forms.length; i<formCount; i++) {
                            applyExtraClasses(forms.eq(i), i);
                            forms.eq(i).find('input,select,textarea,label,div').each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                        preventEmptyFormset(row, forms);
                    }


                    if( forms === undefined ) {
                        var forms = $('.' + options.formCssClass + ':visible').not('.formset-custom-template');
                    } else {
                        forms = $(forms).filter(':visible');
                    }

                    if( options.notEmptyFormSetAddCssClass ) {
                        addButton = $('#id_' + options.prefix + '-TOTAL_FORMS').siblings('.' + options.addCssClass)
                        if (forms.length > 0) {
                            $(addButton).addClass(options.notEmptyFormSetAddCssClass);
                        } else {
                            $(addButton).removeClass(options.notEmptyFormSetAddCssClass);
                        }
                    }

                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                del.remove();
            }
            row.find('label[for $= "-DELETE"]').parent().remove();
            if (hasChildElements(row)) {
                insertDeleteLink(row);
                row.addClass(options.formCssClass);
                applyExtraClasses(row, i);
                var forms = $('.' + options.formCssClass).not('.formset-custom-template');
                preventEmptyFormset(row, forms);
            }
        });

        if ($$.length) {
            var addButton, template;
            if (options.formTemplate) {
                // If a form template was specified, we'll clone it to generate new form instances:
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass).addClass('formset-custom-template');
                template.find('input,select,textarea,label').each(function() {
                    updateElementIndex($(this), options.prefix, 2012);
                });
                insertDeleteLink(template);
            } else {
                // Otherwise, use the last form in the formset; this works much better if you've got
                // extra (>= 1) forms (thnaks to justhamade for pointing this out):
                template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
                template.find('input:hidden[id $= "-DELETE"]').remove();
                template.find('input,select,textarea,label').each(function() {
                    var elem = $(this);
                    // If this is a checkbox or radiobutton, uncheck it.
                    // This fixes Issue 1, reported by Wilson.Andrew.J:
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.attr('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }
            // FIXME: Perhaps using $.data would be a better idea?
            options.formTemplate = template;

            // Otherwise, insert it immediately after the last form:
            $$.filter(':last').after('<a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a>');
            addButton = $$.filter(':last').next();

            addButton.click(function() {
                var formCount = parseInt($('#id_' + options.prefix + '-TOTAL_FORMS').val()),
                    row = options.formTemplate.clone(true).removeClass('formset-custom-template'),
                    buttonRow = $(this).parents('tr.' + options.formCssClass + '-add').get(0) || this;
                applyExtraClasses(row, formCount);

                row.insertBefore($(buttonRow)).show();
                row.find('input,select,textarea,label').each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                $('#id_' + options.prefix + '-TOTAL_FORMS').val(formCount + 1);

                var forms = $('.' + options.formCssClass).not('.formset-custom-template');
                preventEmptyFormset(row, forms);
                if( options.notEmptyFormSetAddCssClass ) {
                    if (forms.length > 0) {
                        $(this).addClass(options.notEmptyFormSetAddCssClass);
                    } else {
                        $(this).removeClass(options.notEmptyFormSetAddCssClass);
                    }
                }

                // Set what to focus on after click
                $(addButton).data('click-focus', $('.' + options.formCssClass + ':visible:last').find(':input:first').attr('id'));

                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row);
                return false;
            });

            // Enable focus on input after click
            addButton.clickFocus();

            var forms = $('.' + options.formCssClass).not('.formset-custom-template');
            if( options.notEmptyFormSetAddCssClass ) {
                if (forms.length > 0) {
                    $(addButton).addClass(options.notEmptyFormSetAddCssClass);
                } else {
                    $(addButton).removeClass(options.notEmptyFormSetAddCssClass);
                }
            }
        }

        return $$;
    }

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        addCssClass: 'add-row',          // CSS class applied to the add link
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        added: null,                     // Function called each time a new form is added
        removed: null,                   // Function called each time a form is deleted
        preventEmptyFormset: false,      // Boolean value whether or not to prevent empty formset
        notEmptyFormSetAddCssClass: '',  // CSS class applied to the add link when formset is not empty
    };
})(jQuery);
