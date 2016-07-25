(function($, window, document) {
    window.HLFormsets = {
        config: {
            formsetClass: '.formset',
        },
        init: function(config) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            $(self.config.formsetClass).formset();
            self.initListeners();
        },

        initListeners: function() {
            var body = $('body');

            body.on('formAdded', '[data-formset-form]', function() {
                var formsetElement = $(this).parents('.formset');
                var addElement = $(formsetElement).find('.add-link');

                var indent = ($(formsetElement).attr('data-formset-indent') || 'true') === 'true';

                if (indent) {
                    $(addElement).find('.form-control-static').addClass('col-md-offset-2').removeClass('form-control-static');
                }
                $(addElement).find('label').addClass('hide');

                if ($(formsetElement).find('[data-formset-form]').length === 1) {
                    $(this).find('label.hide').removeClass('hide');

                    if (indent) {
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
        },
    };
})(jQuery, window, document);
