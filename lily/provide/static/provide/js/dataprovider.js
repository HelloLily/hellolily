(function($, window, document, undefined) {
    window.HLDataProvider = {
        config: {
            buttonDataProvider: ':button.dataprovider',
            loadingText: 'Beaming up the information now, almost within range!',
            loadingHeader: 'I\'m on my way!',
            provideUrl: '/provide/account/',
            dataProviderClass: '.dataprovider',
            errorHeader: 'Oops!',
            errorText: 'There was an error trying to fetch your data, please don\'t be mad.',
            successHeader: 'Yeah!',
            successText: 'We did it! Your new data should be right there waiting for you.',
            hiddenSuccessHeader: 'Psst!',
            hiddenSuccessText: 'Did you know I did more work in the background? ;)',
            overwriteConfirmHeader: 'Do you wish to overwrite the following fields?\n',
            fields: [
                'name',
                'description',
                'legalentity',
                'taxnumber',
                'bankaccountnumber',
                'cocnumber',
                'iban',
                'bic',
            ],
            formsets: [
                'email_addresses',
                'phone_numbers',
                'addresses'
            ]
        },

        init: function(config) {
            // Setup config
            var self = this;
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }

            self.initListeners();
        },

        initListeners: function() {
            var self = this,
                cf = self.config;

            $('body').on('click', cf.buttonDataProvider, function(event) {
                // On button press
                self.findDataProviderInfo.call(self, this, event);
            }).on('keydown', 'div' + cf.dataProviderClass + ' > input', function(event) {
                // Catch ENTER on Dataprovider input
                if (event.which === 13) {
                    self.findDataProviderInfo.call(self, cf.buttonDataProvider, event);
                    // Prevent form submission
                    event.preventDefault();
                }
            });
        },

        findDataProviderInfo: function(button, event) {
            var self = this,
                cf = self.config,
                $button = $(button),
                $form = $button.closest('form'),
                $input = $('div' + cf.dataProviderClass +' > input'),
                domain = self.sanitizeDomain($input.val());

            // Show busy gui to user
            $button.button('loading');
            toastr.info(cf.loadingText, cf.loadingHeader);

            var url = cf.provideUrl + domain;
            $.getJSON(url)
                .done(function(data) {
                    if (data.error) {
                        toastr.error(data.error.message, cf.errorHeader);
                    } else {
                        self.fillForm($form, data, cf.fields, cf.formsets);
                        toastr.success(cf.successText, cf.successHeader);
                    }
                })
                .fail(function() {
                    toastr.error(cf.errorText, cf.errorHeader);
                })
                .always(function() {
                    $button.button('reset');
                });

            event.preventDefault();
        },

        sanitizeDomain: function(url) {
            var domain = $.trim(url.replace('http://', ''));
            domain = $.trim(domain.replace('https://', ''));
            // Always add last '/'
            if (domain.slice(-1) !== '/') {
                domain += '/';
            }
            return domain;
        },

        fillForm: function($form, data, fields, formsets) {
            var self = this,
                cf = self.config;

            var checkOverwrite = self.loopTroughFields(fields, $form, data),
                checkOverwriteFields = checkOverwrite[0],
                checkOverwriteLabels = checkOverwrite[1];

            // Check if there are fields for which we need to do an overwrite check
            if (checkOverwriteFields.length) {
                // Ask the user whether to overwrite or not
                if (confirm(cf.overwriteConfirmHeader + checkOverwriteLabels.join('\n'))) {
                    // Loop through fields that need to be overwritten
                    checkOverwriteFields.forEach(function(field) {
                        var $input = $form.find('[name="' + field + '"]');
                        self.fillField($input, data[field]);
                    });
                }
            }

            // Loop through formsets
            self.loopTroughFormSets(formsets, $form, data);

        },

        loopTroughFields: function(fields, $form, data) {
            var self = this,
                cf = self.config,
                checkOverwriteFields = [],
                checkOverwriteLabels = [],
                filledHiddenField = false;

            // Loop through all fields
            fields.forEach(function(field) {
                // Input is the field in the current form
                var $input = $form.find('[name="' + field + '"]');
                // Always clear the field if it's hidden
                if ($input.attr('type') == 'hidden' || $input.parent().hasClass('hide')) {
                    $input.val('');
                    if (data[field]) {
                        filledHiddenField = true;
                    }
                }
                // Check if there is data for the field, else do nothing
                if (data[field]) {
                    // Check if the field does not exist in the current form
                    if ($input.val() !== undefined) {
                        // Check if the field has a value and that value is not the field placeholder
                        if ($input.val().length && $input.val() !== $input.attr('placeholder')) {
                            // Display label of field instead of field name
                            var label = $input.parents('.form-group').find('label').text();
                            // Field is not empty, check before overwrite
                            checkOverwriteFields.push(field);
                            checkOverwriteLabels.push('- ' + label);
                        } else {
                            // Field is empty, fill it with new data
                            self.fillField($input, data[field]);
                        }
                    }
                }
            });

            if (filledHiddenField) {
                toastr.success(cf.hiddenSuccessText, cf.hiddenSuccessHeader);
            }

            return [checkOverwriteFields, checkOverwriteLabels];
        },

        loopTroughFormSets: function(formsets, $form, data){
            for (var i=0; i < formsets.length; i++) {
                var formset = formsets[i];
                // Check if there is data for the formset
                if (data[formset] && data[formset].length) {
                    var $formsetDiv = $form.find('#' + formset),
                        $formsetAddLink = $formsetDiv.find('[data-formset-add]'),
                        newFormsets = data[formset],
                        $foundInput;

                    for (var j = 0; j < newFormsets.length; j++) {
                        var newFormset = newFormsets[j],
                            insertNewFormset = false,
                            $newElement;

                        if (typeof newFormset === 'object') {
                            var key,
                                hasFoundInput = false;
                            for (key in newFormset) {
                                $foundInput = $formsetDiv.find(':input[name$="' + key +'"]');
                                if ($foundInput.length){
                                    hasFoundInput = true;
                                    $foundInput = $foundInput.filter(function () {
                                        var val = $(this).val(),
                                            newVal = newFormset[key];

                                        return ((val === '' && newVal === null) || val == newVal);
                                    });
                                    if (!$foundInput.length) {
                                        // One of the values is different so we need to add a new formset
                                        insertNewFormset = true;
                                    }
                                }
                            }
                            if (insertNewFormset || !hasFoundInput) {
                                $formsetAddLink.click();
                                $newElement =  $formsetDiv.find('[data-formset-body] [data-formset-form]:last');
                                for (key in newFormset) {
                                    $newElement.find(':input[name$="' + key +'"]').val(newFormset[key]);
                                }
                            }
                        } else if (typeof newFormset === 'string') {
                            $foundInput = $formsetDiv.find(':input').filter(function () {
                                return $(this).val() == newFormset;
                            });
                            if (!$foundInput.length) {
                                $formsetAddLink.click();
                                $newElement =  $formsetDiv.find('[data-formset-body] [data-formset-form]:last');
                                $newElement.find(':input:first').val(newFormset);
                            }
                        }
                    }
                }
            }
        },

        fillField: function($input, value) {
            if (typeof value === 'string') {
                // String
                $input.val(value);
            } else if (typeof value[0] === 'string') {
                // List of strings
                var uniqueValues = value.concat($input.val().split(',')).filter(function(val, index, self) {
                    return (self.indexOf(val) === index) && (val !== '');
                });
                $input.val(uniqueValues.join());
            } else {
                // JSON object
                $input.val(JSON.stringify(value));
            }
            $input.change();
            if ($input.parent().hasClass('original-form-widget') && $input.parent().hasClass('hide')) {
                // show the input, by reusing the click handler as defined in the utils.
                $input.parents(".show-and-hide-input").find('a[data-action="show"]').trigger('click');
            }
        }
    }
})(jQuery, window, document);
