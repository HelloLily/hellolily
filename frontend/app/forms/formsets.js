(function($, window, document, undefined){
    window.HLFormsets = {
        config: {
            formsetClass: '.formset'
        },
        init: function (config) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            $(self.config.formsetClass).formset();
            self.initListeners();
        },

        initListeners: function() {
            var self = this;
            var body = $('body');

            body.on('formAdded', '[data-formset-form]', function() {
                var formset_element = $(this).parents('.formset');
                var add_element = $(formset_element).find('.add-link');

                var indent = ($(formset_element).attr('data-formset-indent') || 'true') == 'true';
                if(indent) {
                    $(add_element).find('.form-control-static').addClass('col-md-offset-2').removeClass('form-control-static');
                }
                $(add_element).find('label').addClass('hide');

                if ($(formset_element).find('[data-formset-form]').length === 1) {
                    $(this).find('label.hide').removeClass('hide');

                    if(indent) {
                        $(this).find('.field_wrapper').removeClass('col-md-offset-2');
                    }
                }
                HLSelect2.init();
            });

            body.on('formDeleted', '[data-formset-form]', function() {
                $(this).stop().slideDown();
                $(this).find(':input:enabled:visible').attr('data-formset-disabled', true).attr('readonly', 'readonly');
                $(this).find('[data-formset-delete-button]').toggleClass('hidden');
                $(this).find('[data-formset-undo-delete]').toggleClass('hidden');
            });

            body.on('click', '[data-formset-form] [data-formset-undo-delete]', function() {
                var formset = $(this).closest('[data-formset-form]');

                formset.find('[data-formset-disabled=true]').removeAttr('data-formset-disabled').removeAttr('readonly');
                formset.find('input[name$="DELETE"]').attr('checked', false).change();
                formset.find('[data-formset-delete-button]').toggleClass('hidden');
                $(this).toggleClass('hidden');
            });

        }
    }
})(jQuery, window, document);
