(function($, window, document, undefined){
    window.HLSelect2 = {
        config: {
            tagInputs: 'input.tags',
            ajaxInputs: 'input.select2ajax',
            tagsAjaxClass: 'tags-ajax',
            ajaxPageLimit: 30,
            clearText: '-- Clear --'
        },

        init: function( config ) {
            var self = this;
            // Setup configuration
            if ($.isPlainObject(config)) {
                $.extend(self.config, config);
            }
            // On initialize, setup select2
            self.setupSelect2();
            self.initListeners();
        },

        initListeners: function() {
            var self = this;
            // When modal is shown, lets instantiate the select2 in the modals
            $(document).on('shown.bs.modal', '.modal', function() {
                self.setupSelect2();
            });
        },

        setupSelect2: function() {
            $('select').select2({
                // at least this many results are needed to enable the search field
                // (9 is the amount at which the user must scroll to see all items)
                minimumResultsForSearch: 9
            });
            this.createTagInputs();
            this.createAjaxInputs();
        },

        createTagInputs: function() {
            // Setup tag inputs
            $(this.config.tagInputs).each(function() {
                var tags = [];
                var $this = $(this);
                if ($this.data('choices')) {
                    tags = $this.data('choices').split(',');
                }
                $this.select2({
                    tags: tags,
                    tokenSeparators: [",", " "]
                });
            });
        },

        createAjaxInputs: function() {
            // Setup inputs that needs remote link
            var self = this,
                cf = self.config;
            $(cf.ajaxInputs).each(function() {
                var $this = $(this);
                var options = {
                    ajax: {
                        cache: true,
                        data: function (term, page) { // page is the one-based page number tracked by Select2
                            var data = null;
                            if ($this.hasClass(cf.tagsAjaxClass)) {
                                data = {
                                    q: term, // search term
                                    filterquery: 'email:*', // only return contacts that have an email address
                                    size: cf.ajaxPageLimit, // page size
                                    page: (page - 1) // page number, zero-based
                                };
                            }
                            else {
                                var term_stripped = term.trim();
                                data = {
                                    filterquery: term_stripped ? 'name:('+term_stripped+')' : '', //search term
                                    size: cf.ajaxPageLimit, // page size
                                    page: (page - 1), // page number, zero-based
                                    sort: '-modified' //sort modified descending
                                };
                            }

                            var filters = $this.data('filter-on');
                            filters.split(',').forEach(function(filter) {
                                if (filter.indexOf('id_') === 0) {
                                    var filter_val = $('#'+filter).val();
                                    var filter_name = filter.substring(3);
                                    if (filter_name.indexOf('case_quickbutton_') === 0) {
	                                    filter_name = filter.substring(20);
                                    }
                                    if (filter_val && filter_val > 0) {
                                        data.filterquery += ' '+filter_name+':'+filter_val;
                                    }
                                } else {
                                    data.type = filter;
                                }
                            });
                            return data;
                        },
                        results: function (data, page) {
                            var more = (page * cf.ajaxPageLimit) < data.total; // whether or not there are more results available

                            if ($this.hasClass(cf.tagsAjaxClass)) {
                                var parsed_data = [];

                                data.hits.forEach(function(hit) {
                                    if ($this.hasClass(cf.tagsAjaxClass)) {
                                        // Only display contacts with an e-mail address
                                        for (var i = 0; i < hit.email.length; i++) {
                                            // The text which is actually used in the application
                                            var used_text = '"' + hit.name + '" <' + hit.email[i] + '>';
                                            // The displayed text
                                            var displayed_text = hit.name + ' <' + hit.email[i] + '>';
                                            parsed_data.push({id: used_text, text: displayed_text});
                                        }
                                    }
                                });

                                // Array elements with empty text can't be added to select2, so manually fill a new array
                                data.hits = parsed_data;
                            }
                            else {
                                data.hits.forEach(function(hit) {
                                    hit.text = hit.name;
                                });
                            }

                            // Add clear option
                            if (page == 1 && !$this.hasClass(cf.tagsAjaxClass)) {
                                data.hits.unshift({id: -1, text:cf.clearText});
                            }
                            return {
                                results: data.hits,
                                more: more
                            };
                        }
                    },
                    initSelection: function (item, callback) {
                        var id = item.val();
                        var text = item.data('selected-text');
                        var data = { id: id, text: text };
                        callback(data);
                    }
                };

                if ($this.hasClass(cf.tagsAjaxClass)) {
                    options.tags = true;
                    options.tokenSeparators = [',', ' '];
                    // Create a new tag if there were no results
                    options.createSearchChoice = function (term, data) {
                        if ($(data).filter(function () {
                            return this.text.localeCompare(term) === 0;
                        }).length === 0) {
                            return {
                                id: term,
                                text: term
                            };
                        }
                    }
                }

                $this.select2(options);
            });
        }
    };

})(jQuery, window, document);
