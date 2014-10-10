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
                        quietMillis: 300,
                        cache: true,
                        data: function (term, page) { // page is the one-based page number tracked by Select2
                            return {
                                q: term, //search term
                                page_limit: self.config.ajaxPageLimit, // page size
                                page: page, // page number
                                filter: $('#'+$this.data('filter-on')).val()
                            };
                        },
                        results: function (data, page) {
                            var more = (page * self.config.ajaxPageLimit) < data.total; // whether or not there are more results available
                            // Add clear option
                            if (page == 1) {
                                data.objects.unshift({id: -1, text:self.config.clearText});
                            }
                            return {
                                results: data.objects,
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
