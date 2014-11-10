(function($, window, document, undefined){
    window.HLSelect2 = {
        config: {
            tagInputs: 'input.tags',
            ajaxInputs: 'input.select2ajax',
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
            var self = this;
            $(self.config.ajaxInputs).each(function() {
                var $this = $(this);
                $this.select2({
                    ajax: {
                        cache: true,
                        data: function (term, page) { // page is the one-based page number tracked by Select2
                            var data = {
                                q: term, //search term
                                size: self.config.ajaxPageLimit, // page size
                                page: (page - 1), // page number, zero-based
                            };
                            var filters = $this.data('filter-on');
                            filters.split(',').forEach(function(filter) {
                                if (filter.indexOf('id_') === 0) {
                                    var filter_val = $('#'+filter).val()
                                    var filter_name = filter.substring(3)
                                    if (filter_name.indexOf('case_quickbutton_') === 0) {
                                        filter_name = filter.substring(20);
                                    }
                                    data[filter_name] = filter_val;
                                } else {
                                    data.type = filter;
                                }
                            });
                            return data;
                        },
                        results: function (data, page) {
                            var more = (page * self.config.ajaxPageLimit) < data.total; // whether or not there are more results available
                            data.hits.forEach(function(hit) {
                               hit.text = hit.name;
                            });
                            // Add clear option
                            if (page == 1) {
                                data.hits.unshift({id: -1, text:self.config.clearText});
                            }
                            return {
                                results: data.hits,
                                more: more
                            }
                        }
                    },
                    initSelection: function (item, callback) {
                        var id = item.val();
                        var text = item.data('selected-text');
                        var data = { id: id, text: text };
                        callback(data);
                    }
                });
            });
        }
    };

})(jQuery, window, document);
